# PDM System Integration Guide

## Quick Start

### Backend Setup
```bash
cd backend
uv sync  # or pip install -e .
python main.py --start_server
```

Backend will run on `http://localhost:5000`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:5173` (Vite default)

## Architecture

```
┌─────────────┐         HTTP REST API          ┌──────────────┐
│  Frontend   │ ◄──────────────────────────► │   Backend    │
│  (Electron) │    GET /api/pdm/status        │   (Flask)    │
│             │    POST /api/pdm/channel      │              │
└─────────────┘                                └──────┬───────┘
                                                       │
                                                       │ USB/Serial
                                                       │
                                                  ┌────▼──────┐
                                                  │   STM32   │
                                                  │  Hardware │
                                                  └───────────┘
```

## Key Changes Made

### Backend (`backend/`)

1. **Removed obsolete files:**
   - `firmware/usb_reader.py` (replaced by modular structure)
   - `firmware/requirements.txt` (moved to pyproject.toml)

2. **Added Flask API endpoints:**
   - `/api/health` - Health check
   - `/api/pdm/status` - Complete PDM data (polled by frontend)
   - `/api/pdm/channels` - All channels
   - `/api/pdm/system` - System info
   - `/api/pdm/channel/<id>/set` - Control channels

3. **Added CORS support:**
   - Installed `flask-cors` dependency
   - Enabled CORS in `api/route.py`

4. **Created data reader module:**
   - `hardware/data_reader.py` - Background thread for continuous USB reading
   - Thread-safe data store with locks

5. **In-memory data store:**
   - Global `pdm_data` dict with system voltage, current, and 8 channels
   - Each channel has: voltage, current, temperature, status

### Frontend (`frontend/src/api/client.ts`)

1. **Added control methods:**
   - `addChannel()` - Maps to `/add_channel`
   - `setChannel()` - Maps to `/set_channel`
   - `getParam()` - Maps to `/get_param`
   - `setCurrent()` - Maps to `/set_current`

2. **Existing methods work as-is:**
   - `getStatus()` - Polls `/api/pdm/status` every second
   - `controlChannel()` - Uses `/api/pdm/channel/<id>/set`

## Data Flow

### Frontend → Backend (Control)
```typescript
// Frontend clicks "Toggle Channel"
pdmApi.controlChannel(channelId, enabled)
  ↓
POST /api/pdm/channel/0/set { "enabled": true }
  ↓
Backend updates pdm_data and sends USB command
  ↓
USB device receives command
```

### Backend → Frontend (Monitoring)
```typescript
// Frontend polls every 1 second
pdmApi.getStatus()
  ↓
GET /api/pdm/status
  ↓
Backend returns pdm_data (with latest values)
  ↓
Frontend updates UI (voltage, current, channel status)
```

## Testing

### Test Backend
```bash
cd backend
curl http://localhost:5000/api/health
curl http://localhost:5000/api/pdm/status
curl -X POST http://localhost:5000/api/pdm/channel/0/set \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### Test Frontend
1. Start backend first
2. Start frontend
3. Open browser to `http://localhost:5173`
4. You should see:
   - System voltage and current
   - 8 channels with controls
   - Real-time updates every second

## Device Configuration

Current device path is hardcoded as `/dev/ttyUSB0` (Linux).

To change:
- **Backend**: Edit default in `api/route.py` → `control_channel_rest()`
- **Hardware**: Windows uses `COM3`, `COM4`, etc. macOS uses `/dev/tty.usbserial-*`

## Next Steps

1. **Connect real hardware:** Update device path in backend
2. **Implement data reader:** Use `data_reader.py` to continuously poll USB
3. **Parse USB responses:** Update `data_reader.py` to parse your binary protocol
4. **Add error handling:** Handle USB disconnects, timeouts
5. **Persist configuration:** Save channel states to file/database

## Troubleshooting

**Frontend can't connect to backend:**
- Check backend is running on port 5000
- Check CORS is enabled in `route.py`
- Check frontend API_BASE_URL in `client.ts`

**Backend can't connect to USB:**
- Check device path (`/dev/ttyUSB0`, `COM3`, etc.)
- Check user has serial port permissions (Linux: add to `dialout` group)
- Check baud rate matches hardware (9600 vs 115200)

**Frontend shows "OFFLINE":**
- Backend not running
- Backend crashed (check terminal for errors)
- Network error (check browser console)

## Project Structure

```
PDM/
├── backend/           # Flask REST API
│   ├── api/          # API routes
│   ├── hardware/     # USB communication
│   ├── firmware/     # Utilities
│   └── main.py       # CLI entry point
├── frontend/         # Electron + React UI
│   ├── src/
│   │   ├── api/      # Backend client
│   │   └── App.tsx   # Main UI
│   └── electron/     # Electron main process
└── INTEGRATION.md    # This file
```

## License

[Your License Here]
