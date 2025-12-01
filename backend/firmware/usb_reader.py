#!/usr/bin/env python3
"""
USB Reader & REST API Server

This script:
1. Reads binary data from USB serial port from STM32 hardware
2. Parses the binary protocol
3. Serves REST API endpoints for the frontend to fetch data

Frontend makes REST API calls to this server to display sensor values.
"""

import serial
import struct
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
from typing import List
from datetime import datetime

# Serial port configuration (overridable via env)
# Prefer READER_PORT, then USB_PORT, else default to COM11
import os
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

# Channel control state
channel_enabled: List[bool] = [True] * 8

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
            print("1. STM32 hardware is connected via USB")
            print("2. Correct COM port is configured")
            print("3. STM32 firmware is running and transmitting data")
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
        # Update in-memory state so UI reflects the change immediately
        ch["status"]["on"] = enabled
        if not enabled:
            ch["current"] = 0.0
        in_use = ch["status"]["on"] and ch.get("current", 0.0) > 0.0
        # Update enable mask
        channel_enabled[channel_id] = enabled

        # TODO: Send command to STM32 hardware via serial to actually control the channel
        # For now, this just updates the UI state
        
        return jsonify({"status": "ok", "channel": channel_id, "enabled": enabled, "in_use": in_use})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pdm/trigger-scenario', methods=['POST'])
def trigger_scenario():
    """Trigger a test scenario - Not implemented for hardware mode"""
    return jsonify({"error": "Test scenarios not available in hardware mode"}), 501

@app.route('/api/pdm/test-scenario', methods=['GET'])
def get_test_scenario():
    """Get current test scenario status - Returns idle for hardware mode"""
    return jsonify({
        "name": "Normal Operation",
        "description": "Hardware monitoring mode",
        "elapsed": 0.0,
        "status": "idle",
        "current_event": "Normal operation"
    })

def main():
    """Main entry point"""
    print("=" * 70)
    print("PDM USB Reader & REST API Server")
    print("=" * 70)
    
    # Start USB reader in background
    usb_reader = USBReader(SERIAL_PORT, BAUD_RATE)
    reader_thread = usb_reader.start()
    
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
