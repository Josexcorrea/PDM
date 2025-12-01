from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import threading

from hardware.protobuf import AvailableChannels, ProtoBuff
from hardware.usb_devices import USBDevices

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

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

# Global data store for frontend (thread-safe)
pdm_data_lock = threading.Lock()
pdm_data = {
    "timestamp": datetime.now().isoformat(),
    "system_voltage": 12.0,
    "total_current": 0.0,
    "channels": [
        {
            "id": i,
            "name": CHANNEL_NAMES[i] if i < len(CHANNEL_NAMES) else f"Channel {i+1}",
            "voltage": 0.0,
            "current": 0.0,
            "temperature": 25.0,
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


@app.post("/add_channel")
def add_channel():
    data = request.get_json(force=True)
    device = data["device"]

    usb_device = USBDevices(9600)
    usb_device.connection(device)
    usb_device.send_msg(ProtoBuff.new_channel())
    usb_device.close_connection()

    return jsonify({"status": "ok", "message": "Channel added"}), 200


@app.post("/set_channel")
def set_channel():
    data = request.get_json(force=True)
    device = data["device"]
    channel = data["channel"]
    status = data["status"]

    usb_device = USBDevices(9600)
    usb_device.connection(device)
    usb_device.send_msg(
        ProtoBuff.set_channel(AvailableChannels(channel), status)
    )
    usb_device.close_connection()

    return jsonify({"status": "ok", "message": "Channel updated"}), 200


@app.post("/get_param")
def get_param():
    data = request.get_json(force=True)
    device = data["device"]
    channel = data["channel"]

    usb_device = USBDevices(9600)
    usb_device.connection(device)
    usb_device.send_msg(
        ProtoBuff.get_params(AvailableChannels(channel))
    )
    resp = usb_device.recv_msg()
    usb_device.close_connection()

    return jsonify({"status": "ok", "response": resp}), 200


@app.post("/set_current")
def set_current():
    data = request.get_json(force=True)
    device = data["device"]
    channel = data["channel"]
    current_limit = data["current"]

    usb_device = USBDevices(9600)
    usb_device.connection(device)
    usb_device.send_msg(
        ProtoBuff.set_current_lmit(AvailableChannels(channel), current_limit)
    )
    usb_device.close_connection()

    return jsonify({"status": "ok", "message": "Current limit set"}), 200


# Frontend data endpoints
@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.get("/api/pdm/status")
def get_status():
    """Return complete system status"""
    with pdm_data_lock:
        return jsonify(pdm_data), 200


@app.get("/api/pdm/channels")
def get_channels():
    """Return all channel data"""
    with pdm_data_lock:
        return jsonify({"channels": pdm_data["channels"]}), 200


@app.post("/api/pdm/channel")
def get_channel():
    """Get specific channel data"""
    data = request.get_json(force=True)
    channel_id = data.get("channelId", 0)
    
    with pdm_data_lock:
        if 0 <= channel_id < len(pdm_data["channels"]):
            return jsonify({"channel": pdm_data["channels"][channel_id]}), 200
    
    return jsonify({"error": "Invalid channel ID"}), 400


@app.get("/api/pdm/system")
def get_system():
    """Return system-level information"""
    with pdm_data_lock:
        active_channels = sum(1 for ch in pdm_data["channels"] if ch["status"]["on"])
        return jsonify({
            "system_voltage": pdm_data["system_voltage"],
            "total_current": pdm_data["total_current"],
            "active_channels": active_channels
        }), 200


@app.post("/api/pdm/channel/<int:channel_id>/set")
def control_channel_rest(channel_id):
    """REST endpoint for channel control (maps to set_channel)"""
    data = request.get_json(force=True)
    enabled = data.get("enabled", False)
    device = data.get("device", "/dev/ttyUSB0")  # Default device
    
    # Update local state
    with pdm_data_lock:
        if 0 <= channel_id < len(pdm_data["channels"]):
            pdm_data["channels"][channel_id]["status"]["on"] = enabled
    
    # Send command to hardware
    try:
        usb_device = USBDevices(9600)
        usb_device.connection(device)
        usb_device.send_msg(
            ProtoBuff.set_channel(AvailableChannels(channel_id + 1), enabled)
        )
        usb_device.close_connection()
        
        return jsonify({
            "status": "ok",
            "channel": channel_id,
            "enabled": enabled,
            "in_use": True
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_server():
    app.run(host="0.0.0.0", port=5000, debug=False)

