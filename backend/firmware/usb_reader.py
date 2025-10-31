#!/usr/bin/env python3
"""
USB Reader & REST API Server

This script:
1. Reads binary data from USB serial port (from STM32 or stm32_sim.py)
2. Parses the binary protocol
3. Serves REST API endpoints for the frontend to fetch data

Frontend makes REST API calls to this server to display sensor values.
"""

import serial
import struct
import time
import json
import os
import math
import random
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
from typing import Dict, List, Optional
from datetime import datetime
from test_cases import get_scenario, TestScenario

# Paths for simulator IPC files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRIGGER_FILE = os.path.join(BASE_DIR, "scenario_trigger.json")
STATUS_FILE = os.path.join(BASE_DIR, "scenario_status.json")
CTRL_FILE = os.path.join(BASE_DIR, "channel_controls.json")

# Serial port configuration (overridable via env)
# Prefer READER_PORT, then USB_PORT, else default to COM11
SERIAL_PORT = os.getenv("READER_PORT", os.getenv("USB_PORT", "COM11"))
BAUD_RATE = int(os.getenv("READER_BAUD", "115200"))

# Channel names
CHANNEL_NAMES = [
    "ECU",
    "Fuel Pump",
    "Ignition Coil",
    "Radiator Fan",
    "Data Logger",
    "Dashboard",
    "Sensors",
    "Starter Motor",
]

# Global data store (thread-safe)
pdm_data = {
    "timestamp": None,
    "system_voltage": 0.0,
    "total_current": 0.0,
    "channels": [
        {
            "id": i,
            "name": CHANNEL_NAMES[i],
            "voltage": 0.0,
            "current": 0.0,
            "temperature": 0.0,
            "status": {
                "on": False,
                "fault": False,
                "over_current": False,
                "over_temp": False,
            }
        }
        for i in range(8)
    ]
}

# Mock/scenario state (used when PDM_MOCK=1)
MOCK_ENABLED = os.getenv("PDM_MOCK", "0").lower() in {"1", "true", "yes"}
# Channel enable mask controlled by UI toggles; default enabled
channel_enabled: List[bool] = [True] * 8
mock_current_scenario: Optional[TestScenario] = None
mock_scenario_started_at: float = 0.0
mock_scenario_status: Dict = {
    "name": "Normal Operation",
    "description": "All systems running normally",
    "elapsed": 0.0,
    "status": "idle",
    "current_event": "Normal operation",
}

class USBReader:
    """Reads and parses binary data from STM32"""
    
    def __init__(self, port: str, baud: int):
        self.port = port
        self.baud = baud
        self.serial = None
        self.running = False
        
    def parse_packet(self, packet: bytes) -> bool:
        """
        Parse 58-byte binary packet:
        [Header(1)] [Ch0-7(7 each)] [Checksum(1)]
        
        Returns True if valid packet, False otherwise
        """
        if len(packet) != 58:
            return False
        
        # Verify header
        if packet[0] != 0xAA:
            return False
        
        # Verify checksum
        checksum = 0
        for byte in packet[:-1]:
            checksum ^= byte
        if checksum != packet[-1]:
            print(f"Checksum mismatch: expected {checksum}, got {packet[-1]}")
            return False
        
        # Parse channel data
        offset = 1  # Skip header
        total_current = 0.0
        
        for i in range(8):
            # Unpack 7 bytes: voltage(2) + current(2) + temp(2) + status(1)
            voltage_mv, current_ma, temp_dec, status_byte = struct.unpack_from('<HHhB', packet, offset)
            offset += 7
            
            # Convert to readable units
            voltage = voltage_mv / 1000.0  # mV to V
            current = current_ma / 1000.0  # mA to A
            temperature = temp_dec / 10.0  # decidegrees to °C
            
            # Apply channel enable override from UI: when disabled, treat as OFF with zero current
            if not channel_enabled[i]:
                on_flag = False
                current = 0.0
            else:
                on_flag = bool(status_byte & 0b00000001)
            
            total_current += current
            
            # Parse status byte (bit flags)
            # Bit 0: On/Off
            # Bit 1: Fault
            # Bit 2: Over-current
            # Bit 3: Over-temperature
            pdm_data["channels"][i].update({
                "voltage": round(voltage, 2),
                "current": round(current, 2),
                "temperature": round(temperature, 1),
                "status": {
                    "on": on_flag,
                    "fault": bool(status_byte & 0b00000010),
                    "over_current": bool(status_byte & 0b00000100),
                    "over_temp": bool(status_byte & 0b00001000),
                }
            })
        
        # Update system-wide values
        pdm_data["system_voltage"] = round(pdm_data["channels"][0]["voltage"], 2)
        pdm_data["total_current"] = round(total_current, 2)
        pdm_data["timestamp"] = datetime.now().isoformat()
        
        return True
    
    def read_loop(self):
        """Continuously read from serial port"""
        print(f"\nStarting USB serial reader...")
        print(f"   Port: {self.port}")
        print(f"   Baud: {self.baud}")
        
        try:
            self.serial = serial.Serial(self.port, self.baud, timeout=1)
            print(f"Serial port opened successfully\n")
            self.running = True
            
            packet_count = 0
            while self.running:
                # Read exactly 58 bytes
                packet = self.serial.read(58)
                
                if len(packet) == 58:
                    if self.parse_packet(packet):
                        packet_count += 1
                        if packet_count % 10 == 0:  # Log every second
                            print(f"[{packet_count:05d}] Received | "
                                  f"V:{pdm_data['system_voltage']:.1f}V | "
                                  f"I:{pdm_data['total_current']:.1f}A | "
                                  f"Active:{sum(1 for ch in pdm_data['channels'] if ch['status']['on'])}/8")
                    else:
                        print("Invalid packet received")
                        
        except serial.SerialException as e:
            print(f"\nERROR: Could not open serial port {self.port}")
            print(f"   {e}")
            print("\nMake sure:")
            print("1. stm32_sim.py is running and sending data")
            print("2. Virtual COM port pair is set up correctly")
            print("3. Port names match (COM10 <-> COM11)")
        except KeyboardInterrupt:
            print("\n\nUSB reader stopped")
        finally:
            self.running = False
            if self.serial and self.serial.is_open:
                self.serial.close()
                print(f"Serial port closed")
    
    def start(self):
        """Start reading in background thread"""
        thread = threading.Thread(target=self.read_loop, daemon=True)
        thread.start()
        return thread

    # ---------------- Mock data (optional) ----------------
    def start_mock(self, hz: int = 10):
        """Start a background thread that generates mock PDM data.

        Enable by setting environment variable PDM_MOCK=1 when launching.
        """
        def _mock_loop():
            print("\n[MOCK] Generating synthetic PDM data (no serial device)")
            t0 = time.time()
            while True:
                t = time.time() - t0
                total_current = 0.0

                # Drive scenario if active
                global mock_current_scenario, mock_scenario_started_at, mock_scenario_status
                scenario_states = None
                if mock_current_scenario is not None:
                    elapsed = time.time() - mock_scenario_started_at
                    if elapsed >= mock_current_scenario.duration:
                        mock_current_scenario = None
                        mock_scenario_status.update({
                            "status": "complete",
                            "elapsed": round(elapsed, 2),
                            "current_event": "Scenario complete",
                        })
                    else:
                        scenario_states = mock_current_scenario.get_channel_states(elapsed)
                        mock_scenario_status.update({
                            "name": mock_current_scenario.name,
                            "description": mock_current_scenario.description,
                            "elapsed": round(elapsed, 2),
                            "status": "active",
                            "current_event": mock_current_scenario.get_event_at_time(elapsed),
                        })

                for i, ch in enumerate(pdm_data["channels"]):
                    # Voltage around 13.6–13.9V with gentle ripple
                    v = 13.75 + 0.15 * math.sin(t * 0.5 + i)
                    # Current: different profiles per channel
                    base = [5.2, 3.5, 4.8, 2.0, 1.2, 0.8, 2.1, 0.0][i]
                    ripple = 0.2 * math.sin(t * (0.3 + 0.1 * i))
                    cur = max(0.0, base + ripple)
                    # Temperature: slow drift
                    temp = 30.0 + 5.0 * math.sin(t * 0.1 + i * 0.2)
                    # Status flags - default state (starter off by default)
                    on = channel_enabled[i] and (i != 7)  # respect UI override AND default state
                    fault = False
                    over_current = cur > base + 1.5
                    over_temp = temp > 75.0
                    # Override with scenario state if present
                    if scenario_states is not None:
                        state = scenario_states[i]
                        v = state.get("voltage", v)
                        cur = state.get("current", cur)
                        temp = state.get("temp", temp)
                        on = bool(state.get("status", 0) & 0b00000001) and channel_enabled[i]
                        fault = bool(state.get("status", 0) & 0b00000010)
                    # Zero current when OFF
                    if not on:
                        cur = 0.0
                    ch.update({
                        "voltage": round(v, 2),
                        "current": round(cur, 2),
                        "temperature": round(temp, 1),
                        "status": {
                            "on": on,
                            "fault": fault,
                            "over_current": over_current,
                            "over_temp": over_temp,
                        },
                    })
                    total_current += cur

                pdm_data["system_voltage"] = round(pdm_data["channels"][0]["voltage"], 2)
                pdm_data["total_current"] = round(total_current, 2)
                pdm_data["timestamp"] = datetime.now().isoformat()
                time.sleep(1.0 / max(1, hz))

        thread = threading.Thread(target=_mock_loop, daemon=True)
        thread.start()
        return thread

# Flask REST API Server
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/pdm/status', methods=['GET'])
def get_pdm_status():
    """Get complete PDM status"""
    return jsonify(pdm_data)

@app.route('/api/pdm/channels', methods=['GET'])
def get_all_channels():
    """Get all channel data"""
    return jsonify({
        "timestamp": pdm_data["timestamp"],
        "channels": pdm_data["channels"]
    })

@app.route('/api/pdm/channel/<int:channel_id>', methods=['GET'])
def get_channel(channel_id):
    """Get specific channel data"""
    if 0 <= channel_id < 8:
        return jsonify({
            "timestamp": pdm_data["timestamp"],
            "channel": pdm_data["channels"][channel_id]
        })
    else:
        return jsonify({"error": "Invalid channel ID. Must be 0-7"}), 400

@app.route('/api/pdm/system', methods=['GET'])
def get_system():
    """Get system-level data"""
    return jsonify({
        "timestamp": pdm_data["timestamp"],
        "system_voltage": pdm_data["system_voltage"],
        "total_current": pdm_data["total_current"],
        "active_channels": sum(1 for ch in pdm_data["channels"] if ch["status"]["on"])
    })

@app.route('/api/pdm/channel/<int:channel_id>/set', methods=['POST'])
def set_channel(channel_id):
    """Enable/disable a channel."""
    if not (0 <= channel_id < 8):
        return jsonify({"error": "Invalid channel ID. Must be 0-7"}), 400
    try:
        data = request.get_json()
        enabled = bool(data.get('enabled'))

        ch = pdm_data["channels"][channel_id]
        # Update in-memory state so UI reflects the change immediately in all modes
        ch["status"]["on"] = enabled
        if not enabled:
            ch["current"] = 0.0
        in_use = ch["status"]["on"] and ch.get("current", 0.0) > 0.0
        # Update enable mask so reader/mock apply the override persistently
        channel_enabled[channel_id] = enabled

        if MOCK_ENABLED:
            # In mock mode this is authoritative
            return jsonify({"status": "ok", "channel": channel_id, "enabled": enabled, "in_use": in_use})
        else:
            # In non-mock (hardware/simulator) mode, this only updates the UI snapshot.
            # Persist a control file for stm32_sim.py to ingest on its next loop
            try:
                with open(CTRL_FILE, 'w', encoding='utf-8') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "channels": channel_enabled,
                    }, f)
            except Exception as e:
                print(f"Failed to write control file: {e}")
            return jsonify({"status": "ok", "channel": channel_id, "enabled": enabled, "in_use": in_use})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pdm/trigger-scenario', methods=['POST'])
def trigger_scenario():
    """Trigger a test scenario in the simulator"""
    try:
        data = request.get_json()
        scenario_id = data.get('scenario_id')
        
        if scenario_id not in [1, 2]:
            return jsonify({"error": "Invalid scenario ID. Must be 1 or 2"}), 400
        if MOCK_ENABLED:
            # Drive scenario locally in mock mode
            global mock_current_scenario, mock_scenario_started_at, mock_scenario_status
            mock_current_scenario = get_scenario(int(scenario_id))
            if mock_current_scenario is None:
                return jsonify({"error": "Scenario not found"}), 404
            mock_scenario_started_at = time.time()
            mock_scenario_status.update({
                "name": mock_current_scenario.name,
                "description": mock_current_scenario.description,
                "elapsed": 0.0,
                "status": "active",
                "current_event": "Starting…",
            })
            return jsonify({"status": "triggered", "scenario_id": scenario_id})
        else:
            # Write trigger file for stm32_sim.py to read
            trigger_data = {
                "command": "scenario",
                "scenario_id": scenario_id,
                "timestamp": datetime.now().isoformat()
            }
            with open(TRIGGER_FILE, 'w', encoding='utf-8') as f:
                json.dump(trigger_data, f)
            return jsonify({"status": "triggered", "scenario_id": scenario_id})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pdm/test-scenario', methods=['GET'])
def get_test_scenario():
    """Get current test scenario status"""
    try:
        if MOCK_ENABLED:
            return jsonify(mock_scenario_status)
        # Read scenario status file written by stm32_sim.py
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                scenario_info = json.load(f)
            return jsonify(scenario_info)
        else:
            return jsonify({
                "name": "Normal Operation",
                "description": "All systems running normally",
                "elapsed": 0.0,
                "status": "idle",
                "current_event": "Normal operation"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    """Main entry point"""
    print("=" * 70)
    print("PDM USB Reader & REST API Server")
    print("=" * 70)
    
    # Start USB reader in background
    usb_reader = USBReader(SERIAL_PORT, BAUD_RATE)
    reader_thread = usb_reader.start()
    if MOCK_ENABLED:
        usb_reader.start_mock(hz=10)
    
    # Give serial reader time to initialize
    time.sleep(2)
    
    # Start Flask API server
    print("\nStarting REST API server...")
    print("   URL: http://localhost:5000")
    print("\nAvailable endpoints:")
    print("   GET /api/health              - Health check")
    print("   GET /api/pdm/status          - Complete PDM status")
    print("   GET /api/pdm/channels        - All channels data")
    print("   GET /api/pdm/channel/<0-7>   - Specific channel")
    print("   GET /api/pdm/system          - System voltage/current")
    print("\n" + "=" * 70)
    print("Frontend can now make REST API calls to fetch data")
    print("Press Ctrl+C to stop\n")
    
    # Disable Flask request logging for performance
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        usb_reader.running = False
        reader_thread.join(timeout=2)

if __name__ == "__main__":
    main()
