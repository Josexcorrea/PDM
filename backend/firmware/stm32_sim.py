#!/usr/bin/env python3
"""
STM32F103 Simulator - Serial (COM) based

Generates realistic 8-channel PDM telemetry and streams 58-byte packets at 10 Hz
over a virtual COM port (default COM10). Listens for scenario triggers written by
the backend (/api/pdm/trigger-scenario) in scenario_trigger.json and publishes
scenario_status.json for the frontend to display.
"""
from __future__ import annotations

import json
import os
import random
import struct
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import serial

# Import scenarios (authoritative module)
from test_cases import get_scenario, list_scenarios

# Files used for simple IPC with the backend/frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRIGGER_FILE = os.path.join(BASE_DIR, "scenario_trigger.json")
STATUS_FILE = os.path.join(BASE_DIR, "scenario_status.json")
CTRL_FILE = os.path.join(BASE_DIR, "channel_controls.json")


@dataclass
class ScenarioInfo:
    name: str = "Normal Operation"
    description: str = "All systems running normally"
    elapsed: float = 0.0
    status: str = "idle"  # idle | active | complete
    current_event: str = "Normal operation"


class STM32Simulator:
    CHANNELS = [
        "ECU",
        "Fuel Pump",
        "Ignition Coil",
        "Radiator Fan",
        "Data Logger",
        "Dashboard",
        "Sensors",
        "Starter Motor",
    ]

    def __init__(self, port: str = "COM10", baud: int = 115200):
        self.port_name = port
        self.baud = baud
        self.ser: Optional[serial.Serial] = None

        # Nominal system voltage
        self.voltage = 13.8

        # Channel state
        self.channels_state: List[Dict] = [
            {"voltage": 13.8, "current": 5.2, "temp": 45.0, "status": 0b00000001},
            {"voltage": 13.8, "current": 3.5, "temp": 38.0, "status": 0b00000001},
            {"voltage": 13.8, "current": 4.8, "temp": 42.0, "status": 0b00000001},
            {"voltage": 13.7, "current": 8.0, "temp": 35.0, "status": 0b00000001},
            {"voltage": 13.8, "current": 1.2, "temp": 32.0, "status": 0b00000001},
            {"voltage": 13.8, "current": 0.8, "temp": 30.0, "status": 0b00000001},
            {"voltage": 13.8, "current": 2.1, "temp": 35.0, "status": 0b00000001},
            {"voltage": 13.7, "current": 0.0, "temp": 28.0, "status": 0b00000000},
        ]

        # Scenario handling
        self.active_scenario = None
        self.scenario_started_at = 0.0
        self.scenario_info = ScenarioInfo()

    # ---------- Scenario handling ----------
    def _load_trigger(self) -> Optional[int]:
        if not os.path.exists(TRIGGER_FILE):
            return None
        try:
            with open(TRIGGER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            scenario_id = int(data.get("scenario_id"))
            return scenario_id
        except Exception as e:
            print(f"[SIM] Failed to read trigger file: {e}")
            return None
        finally:
            # Best-effort remove to avoid retrigger
            try:
                os.remove(TRIGGER_FILE)
            except OSError:
                pass

    def _maybe_start_scenario(self):
        scenario_id = self._load_trigger()
        if scenario_id is None:
            return
        scenario = get_scenario(scenario_id)
        if scenario is None:
            print(f"[SIM] Invalid scenario id: {scenario_id}")
            return
        self.active_scenario = scenario
        self.scenario_started_at = time.time()
        self.scenario_info = ScenarioInfo(
            name=scenario.name,
            description=scenario.description,
            elapsed=0.0,
            status="active",
            current_event="Starting…",
        )
        print(f"\n[SIM] Scenario started: {scenario.name}")

    def _update_scenario_state(self):
        if not self.active_scenario:
            # Idle
            self.scenario_info.status = "idle"
            self.scenario_info.elapsed = 0.0
            self.scenario_info.current_event = "Normal operation"
            return

        elapsed = time.time() - self.scenario_started_at
        self.scenario_info.elapsed = elapsed
        self.scenario_info.status = "active"

        if elapsed >= getattr(self.active_scenario, "duration", 5.0):
            print(f"[SIM] Scenario complete: {self.active_scenario.name}")
            self.active_scenario = None
            self.scenario_info.status = "complete"
            self.scenario_info.current_event = "Scenario complete"
            return

        # Let scenario drive the channels
        try:
            self.channels_state = self.active_scenario.get_channel_states(elapsed)
            self.scenario_info.current_event = self.active_scenario.get_event_at_time(elapsed)
        except Exception as e:
            print(f"[SIM] Scenario error: {e}")
            self.active_scenario = None
            self.scenario_info.status = "idle"

    # ---------- Normal operation updates ----------
    def _update_sensors(self):
        if self.active_scenario:
            return
        # System voltage gently varies
        self.voltage += random.uniform(-0.05, 0.05)
        self.voltage = max(12.5, min(14.5, self.voltage))

        for i, ch in enumerate(self.channels_state):
            is_on = bool(ch["status"] & 0b00000001)
            ch["voltage"] = self.voltage + random.uniform(-0.1, 0.1)
            if is_on:
                if i == 7:  # Starter
                    ch["current"] = random.uniform(80.0, 120.0)
                else:
                    base = [5.2, 3.5, 4.8, 8.0, 1.2, 0.8, 2.1, 100.0][i]
                    ch["current"] = max(0.5, base + random.uniform(-0.3, 0.3))
            else:
                ch["current"] = 0.0

            # Temperature dynamics
            target = 25 + (ch["current"] / 10.0) * 15 if is_on else 25.0
            alpha = 0.05 if is_on else 0.02
            ch["temp"] += (target - ch["temp"]) * alpha
            ch["temp"] = max(20.0, min(100.0, ch["temp"]))

            # Cooling fan auto toggle around average temp
            if i == 3:  # Fan
                avg_temp = sum(c["temp"] for c in self.channels_state) / 8
                if avg_temp > 40.0 and not is_on:
                    ch["status"] = 0b00000001
                elif avg_temp < 35.0 and is_on:
                    ch["status"] = 0b00000000

    def _apply_channel_controls(self):
        """Apply channel on/off overrides from CTRL_FILE if present.
        The file structure is: { "timestamp": "...", "channels": [bool x8] }
        When a channel is False, force status OFF; when True, force ON.
        """
        if not os.path.exists(CTRL_FILE):
            return
        try:
            with open(CTRL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            mask = data.get("channels")
            if isinstance(mask, list) and len(mask) == 8:
                for i, on in enumerate(mask):
                    if bool(on):
                        self.channels_state[i]["status"] = 0b00000001
                    else:
                        self.channels_state[i]["status"] = 0b00000000
        except Exception as e:
            print(f"[SIM] Failed to apply channel controls: {e}")

    # ---------- Packet and IO ----------
    def _make_packet(self) -> bytes:
        packet = bytearray()
        packet.append(0xAA)
        for ch in self.channels_state:
            voltage_mv = int(ch["voltage"] * 1000)
            current_ma = int(ch["current"] * 1000)
            temp_dec = int(ch["temp"] * 10)
            packet.extend(struct.pack("<HHhB", voltage_mv, current_ma, temp_dec, ch["status"]))
        checksum = 0
        for b in packet:
            checksum ^= b
        packet.append(checksum)
        return bytes(packet)

    def _write_status_file(self):
        try:
            total_current = sum(ch["current"] for ch in self.channels_state)
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "name": self.scenario_info.name,
                        "description": self.scenario_info.description,
                        "elapsed": round(self.scenario_info.elapsed, 2),
                        "status": self.scenario_info.status,
                        "current_event": self.scenario_info.current_event,
                        "system_voltage": round(self.channels_state[0]["voltage"], 2),
                        "total_current": round(total_current, 2),
                    },
                    f,
                )
        except Exception as e:
            print(f"[SIM] Failed to write status file: {e}")

    # ---------- Main loop ----------
    def run(self):
        print("=" * 70)
        print("STM32F103 SIMULATOR - Binary USB Serial Transmission")
        print("=" * 70)
        print(f"Port: {self.port_name}  Baud: {self.baud}")
        print("Channels:")
        for i, name in enumerate(self.CHANNELS):
            state = "ON" if self.channels_state[i]["status"] & 0x01 else "OFF"
            print(f"  [{i}] {name:15s} - {state}")
        print("\nAvailable scenarios:")
        for sid, name, desc in list_scenarios():
            print(f"  {sid}: {name} - {desc}")
        print("\nStarting transmission at 10 Hz…\n")

        try:
            self.ser = serial.Serial(self.port_name, self.baud, timeout=1)
        except serial.SerialException as e:
            print(f"\n[SIM] ERROR: Could not open serial port {self.port_name}: {e}")
            print("Ensure a virtual COM pair exists (e.g., COM10<->COM11) and adjust ports.")
            return

        packet_count = 0
        try:
            while True:
                # Check for triggers and update state
                self._maybe_start_scenario()
                self._update_scenario_state()
                self._apply_channel_controls()
                self._update_sensors()

                # Make and send packet
                pkt = self._make_packet()
                self.ser.write(pkt)
                packet_count += 1

                # Status output once per second
                if packet_count % 10 == 0:
                    total_current = sum(ch["current"] for ch in self.channels_state)
                    avg_temp = sum(ch["temp"] for ch in self.channels_state) / 8
                    tag = (
                        f" [{self.scenario_info.status.upper()}]"
                        if self.scenario_info.status != "idle"
                        else ""
                    )
                    print(
                        f"[{packet_count:05d}]{tag} Sent 58 bytes | "
                        f"V:{self.voltage:.1f}V | I:{total_current:.1f}A | T:{avg_temp:.1f}°C"
                    )

                # Publish scenario status for API
                self._write_status_file()

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[SIM] Stopped by user")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("[SIM] Serial port closed")


if __name__ == "__main__":
    # Allow overriding port via env var for convenience
    port = os.getenv("SIM_PORT", "COM10")
    baud = int(os.getenv("SIM_BAUD", "115200"))
    STM32Simulator(port, baud).run()

