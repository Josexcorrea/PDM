# PDM Backend

Power Distribution Module Backend Server - Flask REST API for controlling and monitoring PDM hardware.

## Architecture

```
backend/
├── api/
│   ├── route.py         # Flask REST API endpoints
│   └── channels.py      # (placeholder for future expansion)
├── hardware/
│   ├── commands.py      # CLI command handlers
│   ├── protobuf.py      # Protocol buffer definitions
│   ├── usb_devices.py   # USB communication layer
│   └── data_reader.py   # Background data reading (optional)
├── firmware/            # Firmware-related utilities
├── main.py             # CLI entry point
└── pyproject.toml      # Python dependencies
```

## API Endpoints

### Frontend Data Endpoints (Read-Only)
- `GET /api/health` - Health check
- `GET /api/pdm/status` - Complete system status (voltage, current, all channels)
- `GET /api/pdm/channels` - All channel data
- `POST /api/pdm/channel` - Get specific channel by ID
- `GET /api/pdm/system` - System-level info (voltage, current, active channels)

### Control Endpoints
- `POST /add_channel` - Add a new channel
  ```json
  { "device": "/dev/ttyUSB0" }
  ```
- `POST /set_channel` - Turn channel ON/OFF
  ```json
  { "device": "/dev/ttyUSB0", "channel": 1, "status": true }
  ```
- `POST /get_param` - Get channel parameters
  ```json
  { "device": "/dev/ttyUSB0", "channel": 1 }
  ```
- `POST /set_current` - Set current limit
  ```json
  { "device": "/dev/ttyUSB0", "channel": 1, "current": 5.5 }
  ```
- `POST /api/pdm/channel/<id>/set` - REST-style channel control
  ```json
  { "enabled": true, "device": "/dev/ttyUSB0" }
  ```

## Installation

```bash
# Install dependencies (using uv or pip)
uv sync
# or
pip install -e .
```

## Usage

### Start Server
```bash
# Using CLI
python main.py --start_server

# Or directly
python -m api.route
```

Server runs on `http://0.0.0.0:5000`

### CLI Commands
```bash
# Find devices
python main.py --find_devices

# Add channel
python main.py --add_channel --device ttyUSB0

# Set channel ON/OFF
python main.py --set_channel --device ttyUSB0 --channel_number 1 --status True

# Get channel parameters
python main.py --get_params --device ttyUSB0 --channel_number 1

# Set current limit
python main.py --set_current --device ttyUSB0 --channel_number 1 --current_limit 5.5
```

## Configuration

- **Baud Rate**: 9600 (default) / 115200 (device communication)
- **Port**: 5000
- **CORS**: Enabled for frontend communication
- **Default Device**: `/dev/ttyUSB0` (Linux) - adjust for your OS

## Frontend Integration

The backend is designed to work with the Electron + React frontend in `../frontend/`.

The frontend polls `/api/pdm/status` every second to get real-time data.

Channel control is done via `/api/pdm/channel/<id>/set` endpoint.

## Development Notes

- **Thread-safe**: Uses `threading.Lock` for concurrent access to `pdm_data`
- **Mock Data**: Currently returns mock data - integrate `data_reader.py` for real USB reading
- **Protocol**: Uses custom binary protocol defined in `protobuf.py`
- **Channels**: 8 channels (0-7) with names: ECU, Fuel Pump, Ignition Coil, etc.

## Dependencies

- Flask >= 3.1.2
- Flask-CORS >= 4.0.0
- pyserial >= 3.5
- click >= 8.3.0
- clippy >= 0.6.4
