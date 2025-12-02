 # PDM - Power Distribution Module
 
 Desktop application for monitoring a Power Distribution Module (PDM) in an FSAE race car.
 
 - Simulator: Python script generates 8‑channel telemetry over a virtual COM port
 - Backend API: Python Flask parses binary packets and serves REST endpoints
 - Frontend: Electron + React (Vite + Tailwind) dashboard UI
 - Rust: Placeholder for a future backend implementation
 
## Frontend theme
- The UI uses Tailwind CSS + DaisyUI with a custom FIU theme.
- Themes: `fiu` (light) and `fiu-dark` (dark, default). You can still switch to stock themes if desired.
- Use the header toggle to switch between FIU Light/Dark. Preference is saved to localStorage.

 ## Requirements
 - Windows (tested) with a virtual COM pair (e.g., COM10 <-> COM11 via com0com)
 - Python 3.8+
 - Node.js 18+
 
 ## Quick start
 One command to run the entire stack (simulator + API + UI):
 
 1) Install dependencies
 
 ```powershell
 cd "backend/firmware"
 pip install -r requirements.txt
 
 cd "../../frontend"
 npm install
 ```
 
 2) Run app (all services):
 
 ```powershell
 cd "frontend"
 npm run dev
 # Starts simulator (COM10), API (http://localhost:5000), Vite (5173), Electron
 ```
 
 ## REST API (selected)
 - GET /api/health — Health check
 - GET /api/pdm/status — Full system snapshot (voltage, total current, 8 channels)
 - GET /api/pdm/system — System summary
 - POST /api/pdm/trigger-scenario — Body: { "scenario_id": 1|2 }
 - GET /api/pdm/test-scenario — Current scenario status
 
 ## Simulator details
 - Port: COM10 (configurable via SIM_PORT env var)
 - Packet: 58 bytes — 1 header (0xAA) + 8 channels x 7 bytes + 1 checksum (XOR)
 - Channel: 7 bytes = voltage mV (u16) + current mA (u16) + temp 0.1°C (i16) + status flags (u8)
 - Scenarios: Cooling Fan Failure (1), Engine Start Sequence (2)
 - Trigger file: backend/firmware/scenario_trigger.json (written by API)
 - Status file: backend/firmware/scenario_status.json (read by API)
 
 ## Project structure
 ```
 PDM/
   backend/
     firmware/
       stm32_sim.py       # Serial simulator (COM10)
       usb_reader.py      # Serial reader + Flask REST API (port 5000)
       requirements.txt   # Python deps
  test_cases.py      # Test scenarios
     rust/
       main.rs            # Placeholder executable
       lib.rs             # Placeholder library
     Cargo.toml           # Rust project (dependencies empty for now)
   frontend/
     electron/
       main.js            # Electron main process
       preload.js         # Preload script
     src/
       App.tsx            # Dashboard UI
       main.tsx           # React entry
       api/client.ts      # REST client
     index.html           # Vite entry
     package.json         # Frontend deps and scripts
 ```
 
 ## Switching to real hardware
 Edit `backend/firmware/usb_reader.py` and set the actual COM port:
 
 ```python
 SERIAL_PORT = "COM3"  # Example real device port
 ```
 
 Ensure the firmware emits the same 58‑byte packet format over USB CDC.
 
 ## License
 MIT



FSAE race car power distribution monitoring system with STM32 microcontroller, Python backend, and React frontend.



backend/Cargo.toml is Rust project configuration.FSAE race car power distribution monitoring system with STM32 microcontroller, Python backend, and React frontend.



backend/firmware/requirements.txt contains Python dependencies.



backend/firmware/test_cases.py defines test scenarios for the simulator. Contains CoolingFanFailure and EngineStartSequence scenarios that simulate realistic race conditions over 5 seconds then return to normal operation.backend/Cargo.toml is Rust project configuration.FSAE race car power distribution monitoring system with STM32 microcontroller, Python backend, and React frontend.FSAE race car power distribution monitoring system with STM32 microcontroller, Python backend, and React frontend.



backend/firmware/stm32_sim.py simulates STM32F103 hardware, generates sensor data and sends binary packets to COM10 at 10 Hz. Monitors scenario_trigger.json for commands from frontend, executes test scenarios, and writes scenario status to scenario_status.json for the API to read.



backend/firmware/usb_reader.py reads serial from COM11, parses packets, serves REST API on port 5000 with Flask routes for health, status, channels, system data, scenario triggering, and scenario status.backend/firmware/requirements.txt contains Python dependencies.



backend/rust/main.rs and lib.rs are placeholders for future Rust implementation.



frontend/src/App.tsx is the main dashboard UI that polls the API every 500ms, displays 8 channels, and includes test scenario control box in bottom-right corner with buttons to trigger scenarios and view real-time scenario events.backend/firmware/stm32_sim.py simulates STM32F103 hardware, generates sensor data and sends binary packets to COM10 at 10 Hz.backend/Cargo.toml is the Rust project configuration file.FSAE race car power distribution monitoring system with STM32 microcontroller, Python backend, and React frontend.



frontend/src/api/client.ts is the REST API wrapper that fetches data from localhost:5000 and includes triggerScenario and getTestScenario methods for test scenario control.



frontend/index.html is the HTML entry point.backend/firmware/usb_reader.py reads serial from COM11, parses packets, serves REST API on port 5000 with Flask routes for health, status, channels, and system data.



frontend/electron/main.js and preload.js handle the Electron desktop app.


backend/rust/main.rs and lib.rs are placeholders for future Rust implementation.backend/firmware/requirements.txt contains Python dependencies for backend.## Project Files



frontend/src/App.tsx is the main dashboard UI that polls the API every 500ms and displays 8 channels.



frontend/src/api/client.ts is the REST API wrapper that fetches data from localhost:5000.backend/firmware/stm32_sim.py simulates STM32F103 microcontroller hardware. It has update_sensors() which generates random voltage, current, temperature values for 8 channels, create_binary_packet() which packs sensor data into 58-byte binary format, and run() which sends packets over virtual serial port COM10 at 10 Hz. Sends to COM10 virtual serial port, receives from none.FSAE race car power distribution monitoring system with STM32 microcontroller, Python backend, and React frontend.



frontend/index.html is the HTML entry point.



frontend/electron/main.js and preload.js handle the Electron desktop app.backend/firmware/usb_reader.py reads serial data and serves REST API. It has parse_packet() which unpacks 58-byte binary packets and validates checksum, read_loop() which continuously reads from serial port and updates global data, start() which runs serial reader in background thread, and Flask routes /api/health, /api/pdm/status, /api/pdm/channels, /api/pdm/channel/<id>, /api/pdm/system. Receives from COM11 paired with COM10, sends to frontend via REST API on port 5000.### backend/Cargo.toml




backend/rust/main.rs is a placeholder for future Rust backend implementation.Rust project configuration file.## Project Files



backend/rust/lib.rs is a placeholder for future Rust library.



frontend/src/App.tsx is the main React UI component for dashboard. It has fetchSystemStatus() which polls REST API every 500ms, handleResetAll() which is a placeholder for emergency shutdown, handleSaveConfig() which saves current configuration, toggleChannel() which is a placeholder for channel control, and displays 8 channels with voltage, current, temperature. Receives from http://localhost:5000/api/pdm/status, sends to none currently read-only.### backend/firmware/requirements.txtFSAE race car power distribution monitoring system with STM32 microcontroller, Python backend, and React frontend.



frontend/src/api/client.ts is the REST API client wrapper. It has getStatus() which fetches complete PDM status, getChannels() which fetches all channel data, getChannel(id) which fetches single channel, and getSystemInfo() which fetches system voltage/current. Receives from http://localhost:5000/api, sends to App.tsx components.Python dependencies for backend.



frontend/index.html is the main HTML entry point for React app.### backend/Cargo.toml



frontend/electron/main.js is the Electron desktop application main process.### backend/firmware/stm32_sim.py



frontend/electron/preload.js is the Electron preload script for security context.Simulates STM32F103 microcontroller hardware.Rust project configuration file.## Project Files


Functions: update_sensors() generates random voltage, current, temperature values for 8 channels, create_binary_packet() packs sensor data into 58-byte binary format, run() sends packets over virtual serial port COM10 at 10 Hz.

Data flow: Sends to COM10 virtual serial port, receives from none.



### backend/firmware/usb_reader.py### backend/firmware/requirements.txt

Reads serial data and serves REST API.

Functions: parse_packet() unpacks 58-byte binary packets and validates checksum, read_loop() continuously reads from serial port and updates global data, start() runs serial reader in background thread, Flask routes /api/health, /api/pdm/status, /api/pdm/channels, /api/pdm/channel/<id>, /api/pdm/system.Python dependencies for backend.

Data flow: Receives from COM11 paired with COM10, sends to frontend via REST API on port 5000.

### backend/firmware/stm32_sim.py

### backend/rust/main.rs

Placeholder for future Rust backend implementation.### backend/firmware/stm32_sim.py



### backend/rust/lib.rsSimulates STM32F103 microcontroller hardware.Simulates STM32F103 microcontroller hardware.## Quick Start

Placeholder for future Rust library.

Functions:

### frontend/src/App.tsx

Main React UI component for dashboard.- `update_sensors()` - Generates random voltage, current, temperature values for 8 channelsFunctions:

Functions: fetchSystemStatus() polls REST API every 500ms, handleResetAll() placeholder for emergency shutdown, handleSaveConfig() saves current configuration, toggleChannel() placeholder for channel control, displays 8 channels with voltage, current, temperature.

Data flow: Receives from http://localhost:5000/api/pdm/status, sends to none currently read-only.- `create_binary_packet()` - Packs sensor data into 58-byte binary format



### frontend/src/api/client.ts- `run()` - Sends packets over virtual serial port COM10 at 10 Hz- `update_sensors()` - Generates random voltage, current, temperature values for 8 channels```powershellFSAE race car power distribution monitoring system with STM32 microcontroller, Python backend, and React frontend.

REST API client wrapper.

Functions: getStatus() fetches complete PDM status, getChannels() fetches all channel data, getChannel(id) fetches single channel, getSystemInfo() fetches system voltage/current.Data flow:

Data flow: Receives from http://localhost:5000/api, sends to App.tsx components.

- Sends to: COM10 (virtual serial port)- `create_binary_packet()` - Packs sensor data into 58-byte binary format

### frontend/index.html

Main HTML entry point for React app.- Receives from: None



### frontend/electron/main.js- `run()` - Sends packets over virtual serial port COM10 at 10 Hz# Terminal 1 - Simulator

Electron desktop application main process.

### backend/firmware/usb_reader.py

### frontend/electron/preload.js

Electron preload script for security context.Reads serial data and serves REST API.Data flow:


Functions:

- `parse_packet()` - Unpacks 58-byte binary packets, validates checksum- Sends to: COM10 (virtual serial port)cd backend\firmware

- `read_loop()` - Continuously reads from serial port, updates global data

- `start()` - Runs serial reader in background thread- Receives from: None

- Flask routes: `/api/health`, `/api/pdm/status`, `/api/pdm/channels`, `/api/pdm/channel/<id>`, `/api/pdm/system`

Data flow:python stm32_sim.py

- Receives from: COM11 (paired with COM10)

- Sends to: Frontend via REST API on port 5000### backend/firmware/usb_reader.py



### backend/rust/main.rsReads serial data and serves REST API.## Quick Start**FSAE Power Distribution Module with Real-Time Monitoring**

Placeholder for future Rust backend implementation.

Functions:

### backend/rust/lib.rs

Placeholder for future Rust library.- `parse_packet()` - Unpacks 58-byte binary packets, validates checksum# Terminal 2 - Backend API



### frontend/src/App.tsx- `read_loop()` - Continuously reads from serial port, updates global data

Main React UI component for dashboard.

Functions:- `start()` - Runs serial reader in background threadcd backend\firmware

- `fetchSystemStatus()` - Polls REST API every 500ms

- `handleResetAll()` - Placeholder for emergency shutdown- Flask routes: `/api/health`, `/api/pdm/status`, `/api/pdm/channels`, `/api/pdm/channel/<id>`, `/api/pdm/system`

- `handleSaveConfig()` - Saves current configuration

- `toggleChannel()` - Placeholder for channel controlData flow:python usb_reader.py

- Displays 8 channels with voltage, current, temperature

Data flow:- Receives from: COM11 (paired with COM10)

- Receives from: `http://localhost:5000/api/pdm/status`

- Sends to: None (read-only currently)- Sends to: Frontend via REST API on port 5000```powershell



### frontend/src/api/client.ts

REST API client wrapper.

Functions:### frontend/src/App.tsx# Terminal 3 - Frontend

- `getStatus()` - Fetches complete PDM status

- `getChannels()` - Fetches all channel dataMain React UI component for dashboard.

- `getChannel(id)` - Fetches single channel

- `getSystemInfo()` - Fetches system voltage/currentFunctions:cd frontend# Terminal 1 - Simulator

Data flow:

- Receives from: `http://localhost:5000/api`- `fetchSystemStatus()` - Polls REST API every 500ms

- Sends to: App.tsx components

- `handleResetAll()` - Placeholder for emergency shutdownnpm run dev

### frontend/index.html

Main HTML entry point for React app.- `handleSaveConfig()` - Saves current configuration



### frontend/electron/main.js- `toggleChannel()` - Placeholder for channel control```cd backend\firmwareA complete system for monitoring and controlling power distribution in a Formula SAE race car. The system reads sensor data from an STM32F103 microcontroller via USB and displays it in a modern desktop application.**FSAE Power Distribution Module with Real-Time Monitoring**

Electron desktop application main process.

- Displays 8 channels with voltage, current, temperature

### frontend/electron/preload.js

Electron preload script for security context.Data flow:


- Receives from: `http://localhost:5000/api/pdm/status`

- Sends to: None (read-only currently)## Project Filespython stm32_sim.py



### frontend/src/api/client.ts

REST API client wrapper.

Functions:### backend/firmware/stm32_sim.py

- `getStatus()` - Fetches complete PDM status

- `getChannels()` - Fetches all channel dataSimulates STM32F103 microcontroller hardware.

- `getChannel(id)` - Fetches single channel

- `getSystemInfo()` - Fetches system voltage/currentFunctions:# Terminal 2 - Backend API

Data flow:

- Receives from: `http://localhost:5000/api`- `update_sensors()` - Generates random voltage, current, temperature values for 8 channels

- Sends to: App.tsx components

- `create_binary_packet()` - Packs sensor data into 58-byte binary formatcd backend\firmware## System Architecture

### backend/rust/main.rs

Placeholder for future Rust backend implementation.- `run()` - Sends packets over virtual serial port COM10 at 10 Hz

Functions:

- None (just comments)Data flow:python usb_reader.py

Data flow:

- Not currently used- Sends to: COM10 (virtual serial port)



### backend/rust/lib.rs- Receives from: None

Placeholder for future Rust library.

Functions:

- None (just comments)

Data flow:### backend/firmware/usb_reader.py# Terminal 3 - Frontend

- Not currently used

Reads serial data and serves REST API.

Functions:cd frontend```A complete system for monitoring and controlling power distribution in a Formula SAE race car. The system reads sensor data from an STM32F103 microcontroller via USB and displays it in a modern desktop application.**FSAE Power Distribution Module with Real-Time Monitoring**

- `parse_packet()` - Unpacks 58-byte binary packets, validates checksum

- `read_loop()` - Continuously reads from serial port, updates global datanpm run dev

- `start()` - Runs serial reader in background thread

- Flask routes: `/api/health`, `/api/pdm/status`, `/api/pdm/channels`, `/api/pdm/channel/<id>`, `/api/pdm/system````┌─────────────────┐

Data flow:

- Receives from: COM11 (paired with COM10)

- Sends to: Frontend via REST API on port 5000

## Project Files│   STM32F103     │  ← Reads sensors (voltage, current, temp)

### frontend/src/App.tsx

Main React UI component for dashboard.

Functions:

- `fetchSystemStatus()` - Polls REST API every 500ms### backend/firmware/stm32_sim.py│  Microcontroller│  ← Controls 8 power channels

- `handleResetAll()` - Placeholder for emergency shutdown

- `handleSaveConfig()` - Saves current configurationSimulates STM32F103 microcontroller hardware.

- `toggleChannel()` - Placeholder for channel control

- Displays 8 channels with voltage, current, temperature└────────┬────────┘---

Data flow:

- Receives from: `http://localhost:5000/api/pdm/status`Functions:

- Sends to: None (read-only currently)

- `update_sensors()` - Generates random voltage, current, temperature values for 8 channels         │ USB Serial (Binary Protocol, 115200 baud)

### frontend/src/api/client.ts

REST API client wrapper.- `create_binary_packet()` - Packs sensor data into 58-byte binary format

Functions:

- `getStatus()` - Fetches complete PDM status- `run()` - Sends packets over virtual serial port COM10 at 10 Hz         ↓

- `getChannels()` - Fetches all channel data

- `getChannel(id)` - Fetches single channel

- `getSystemInfo()` - Fetches system voltage/current

Data flow:Data flow:┌─────────────────┐

- Receives from: `http://localhost:5000/api`

- Sends to: App.tsx components- Sends to: COM10 (virtual serial port)



### backend/rust/main.rs- Receives from: None│  stm32_sim.py   │  ← [SIMULATION] Generates fake sensor data## System ArchitectureA complete system for monitoring and controlling power distribution in a Formula SAE race car. The system reads sensor data from an STM32F103 microcontroller via USB and displays it in a modern desktop application.Automotive power distribution control system with REST API and real-time monitoring.

Placeholder for future Rust backend implementation.

Functions:

- None (just comments)

Data flow:### backend/firmware/usb_reader.py└────────┬────────┘

- Not currently used

Reads serial data and serves REST API.

### backend/rust/lib.rs

Placeholder for future Rust library.         │ Virtual COM Port (COM10 ↔ COM11)

Functions:

- None (just comments)Functions:

Data flow:

- Not currently used- `parse_packet()` - Unpacks 58-byte binary packets, validates checksum         ↓



## Binary Protocol- `read_loop()` - Continuously reads from serial port, updates global data

58-byte packet structure:

- Byte 0: Header (0xAA)- `start()` - Runs serial reader in background thread┌─────────────────┐```

- Bytes 1-56: 8 channels x 7 bytes each (voltage uint16, current uint16, temperature int16, status uint8)

- Byte 57: XOR checksum- Flask routes: `/api/health`, `/api/pdm/status`, `/api/pdm/channels`, `/api/pdm/channel/<id>`, `/api/pdm/system`



## Installation│  usb_reader.py  │  ← Reads binary packets

```powershell

# Python dependenciesData flow:

cd backend\firmware

pip install -r requirements.txt- Receives from: COM11 (paired with COM10)│                 │  ← Parses sensor data┌─────────────────┐



# Frontend dependencies- Sends to: Frontend via REST API on port 5000

cd frontend

npm install│  (Python/Flask) │  ← Serves REST API (port 5000)

```

Requires virtual COM port software:### frontend/src/App.tsx

- Windows: com0com (COM10 paired with COM11)

- Linux: socatMain React UI component for dashboard.└────────┬────────┘│   STM32F103     │  ← Reads sensors (voltage, current, temp)---



## Switching to Real Hardware

Edit `backend/firmware/usb_reader.py`:

```pythonFunctions:         │ HTTP REST API

SERIAL_PORT = "COM3"  # Change from COM11 to real STM32 port

```- `fetchSystemStatus()` - Polls REST API every 500ms

Flash STM32 with firmware that sends same 58-byte packet format over USB CDC.

- `handleResetAll()` - Placeholder for emergency shutdown         ↓│  Microcontroller│  ← Controls 8 power channels

## License

MIT License- `handleSaveConfig()` - Saves current configuration


- `toggleChannel()` - Placeholder for channel control┌─────────────────┐

- Displays 8 channels with voltage, current, temperature

│   Frontend      │  ← React + TypeScript└────────┬────────┘

Data flow:

- Receives from: `http://localhost:5000/api/pdm/status`│   (Electron)    │  ← Real-time dashboard

- Sends to: None (read-only currently)

│                 │  ← Channel controls         │ USB Serial (Binary Protocol, 115200 baud)

### frontend/src/api/client.ts

REST API client wrapper.└─────────────────┘



Functions:```         ↓## 🏎️ System Architecture## Quick Start**Professional automotive power distribution control system for racing and high-performance vehicles**A Power Distribution Module (PDM) desktop application built with Electron, React, and Rust for hardware communication.

- `getStatus()` - Fetches complete PDM status

- `getChannels()` - Fetches all channel data

- `getChannel(id)` - Fetches single channel

- `getSystemInfo()` - Fetches system voltage/current## Quick Start┌─────────────────┐



Data flow:

- Receives from: `http://localhost:5000/api`

- Sends to: App.tsx components### Prerequisites│  stm32_sim.py   │  ← [SIMULATION] Generates fake sensor data



### backend/rust/main.rs- **Python 3.8+** (for backend)

Placeholder for future Rust backend implementation.

- **Node.js 18+** (for frontend)└────────┬────────┘

Functions:

- None (just comments)- **Virtual COM Port Software** (for simulation):



Data flow:  - Windows: [com0com](https://sourceforge.net/projects/com0com/)         │ Virtual COM Port (COM10 ↔ COM11)```

- Not currently used

  - Linux: `socat` (built-in)

### backend/rust/lib.rs

Placeholder for future Rust library.         ↓



Functions:### Installation

- None (just comments)

┌─────────────────┐┌─────────────────┐

Data flow:

- Not currently used```powershell



## Binary Protocol# 1. Install Python dependencies│  usb_reader.py  │  ← Reads binary packets



58-byte packet structure:cd backend\firmware

- Byte 0: Header (0xAA)

- Bytes 1-56: 8 channels x 7 bytes each (voltage uint16, current uint16, temperature int16, status uint8)pip install -r requirements.txt│                 │  ← Parses sensor data│   STM32F103     │  ← Reads sensors (voltage, current, temp)```bash

- Byte 57: XOR checksum



## Installation

# 2. Install frontend dependencies│  (Python/Flask) │  ← Serves REST API (port 5000)

```powershell

# Python dependenciescd ..\..\frontend

cd backend\firmware

pip install -r requirements.txtnpm install└────────┬────────┘│   Microcontroller │  ← Controls 8 power channels



# Frontend dependencies```

cd frontend

npm install         │ HTTP REST API

```

### Running the System

Requires virtual COM port software:

- Windows: com0com (COM10 paired with COM11)         ↓└────────┬────────┘# Terminal 1 - Backend Server

- Linux: socat

You need to run **3 terminals**:

## Switching to Real Hardware

┌─────────────────┐

Edit `backend/firmware/usb_reader.py`:

```python**Terminal 1: STM32 Simulator**

SERIAL_PORT = "COM3"  # Change from COM11 to real STM32 port

``````powershell│   Frontend      │  ← React + TypeScript         │ USB Serial (Binary Protocol, 115200 baud)



Flash STM32 with firmware that sends same 58-byte packet format over USB CDC.cd backend\firmware



## Licensepython stm32_sim.py│   (Electron)    │  ← Real-time dashboard



MIT License```


│                 │  ← Channel controls         ↓cd backend## 🚀 Quick Start## Architecture

**Terminal 2: USB Reader & API Server**

```powershell└─────────────────┘

cd backend\firmware

python usb_reader.py```┌─────────────────┐

```



**Terminal 3: Frontend UI**

```powershell---│  stm32_sim.py   │  ← [SIMULATION] Generates fake sensor datacargo run

cd frontend

npm run dev

```

## Quick Start└────────┬────────┘

## Project Structure



```

PDM/### Prerequisites         │ Virtual COM Port (e.g., COM10)

├── README.md

├── backend/

│   ├── Cargo.toml              # Rust dependencies (placeholder)

│   ├── rust/                   # Rust source (placeholder)- **Python 3.8+** (for backend)         ↓

│   │   ├── main.rs

│   │   └── lib.rs- **Node.js 18+** (for frontend)

│   └── firmware/               # Python implementation (CURRENT)

│       ├── stm32_sim.py       # STM32 simulator- **Virtual COM Port Software** (for simulation):┌─────────────────┐# Terminal 2 - Frontend UI

│       ├── usb_reader.py      # USB reader + REST API

│       └── requirements.txt  - Windows: [com0com](https://sourceforge.net/projects/com0com/)

└── frontend/

    ├── package.json  - Linux: `socat` (built-in)│ usb_reader.py   │  ← Reads USB serial data

    ├── src/

    │   ├── App.tsx

    │   ├── main.tsx

    │   └── api/### Installation│                 │  ← Parses binary packetscd frontend```bash```

    │       └── client.ts

    └── electron/

        ├── main.js

        └── preload.js```powershell│  (Python)       │  ← Serves REST API on port 5000

```

# 1. Install Python dependencies

## The 8 Power Channels

cd backend\firmware└────────┬────────┘npm install  # First time only

| Ch | Name | Function | Typical Load |

|----|------|----------|--------------|pip install -r requirements.txt

| 1 | ECU | Engine Control Unit | 5-10A |

| 2 | Fuel Pump | High-pressure fuel delivery | 8-12A |         │ HTTP REST API

| 3 | Ignition | Spark/coil system | 3-5A |

| 4 | Cooling Fan | Radiator cooling | 10-15A |# 2. Install frontend dependencies

| 5 | Data Acquisition | Logging system | 2-4A |

| 6 | Dashboard | Display & instruments | 1-3A |cd ..\..\frontend         ↓npm run dev# Terminal 1: Backendpdm/

| 7 | Sensors | Various vehicle sensors | 1-2A |

| 8 | Starter Motor | Engine cranking | 50-80A (brief) |npm install



### Channel Data Format```┌─────────────────┐

Each channel provides:

- **Voltage**: 0-16V (in volts)

- **Current**: 0-50A (in amps)

- **Temperature**: -40 to 125°C (in degrees Celsius)### Running the System│   Frontend      │  ← Makes API calls to fetch data```

- **Status**: Object with flags (`on`, `fault`, `over_current`, `over_temp`)



## USB Communication Protocol

You need to run **3 terminals**:│  (React + Vite) │  ← Displays real-time data in UI

### Binary Packet Format (58 bytes)



```

Byte  | Field              | Type    | Description#### Terminal 1: STM32 Simulator (Fake Hardware)│  (Electron)     │  ← Desktop applicationcd backend├── frontend/           # Electron + React frontend

------|--------------------|---------|----------------------------------

0     | Header             | uint8   | Always 0xAA```powershell

1-2   | CH1 Voltage        | uint16  | Millivolts (0-16000)

3-4   | CH1 Current        | uint16  | Milliamps (0-50000)cd backend\firmware└─────────────────┘

5-6   | CH1 Temperature    | int16   | Decidegrees C (-400 to 1250)

7     | CH1 Status         | uint8   | Bit flagspython stm32_sim.py

8-14  | CH2 Data           | 7 bytes | Same format

15-21 | CH3 Data           | 7 bytes | Same format``````Access the dashboard at http://localhost:5173

22-28 | CH4 Data           | 7 bytes | Same format

29-35 | CH5 Data           | 7 bytes | Same format

36-42 | CH6 Data           | 7 bytes | Same format

43-49 | CH7 Data           | 7 bytes | Same format**What it does:**

50-56 | CH8 Data           | 7 bytes | Same format

57    | Checksum           | uint8   | XOR of all previous bytes- Simulates STM32F103 microcontroller

```

- Generates realistic sensor data (voltage, current, temperature)---cargo run│   ├── electron/       # Electron main process

### Status Byte Bit Flags

- Sends binary packets over virtual serial port (COM10)

```

Bit | Flag         | Description- Updates at 10 Hz

----|--------------|----------------------------------

0   | ON           | Channel is powered on

1   | FAULT        | General fault condition

2   | OVER_CURRENT | Current exceeded threshold#### Terminal 2: USB Reader & API Server## 📁 Project Structure## System Overview

3   | OVER_TEMP    | Temperature exceeded threshold

4-7 | Reserved     | Future use```powershell

```

cd backend\firmware

## REST API Endpoints

python usb_reader.py

Base URL: `http://localhost:5000/api`

``````│   ├── src/           # React source code

### GET /health

Health check endpoint.



**Response:****What it does:**PDM/

```json

{- Reads binary data from virtual serial port (COM11)

  "status": "ok",

  "timestamp": "2025-10-30T12:34:56.789Z"- Parses 58-byte packets├── backend/The PDM system consists of three main components:

}

```- Serves REST API on `http://localhost:5000`



### GET /pdm/status- Provides endpoints for frontend to fetch data│   ├── firmware/                    # Python backend (CURRENT IMPLEMENTATION)

Get complete PDM status (all data).



**Response:**

```json#### Terminal 3: Frontend UI│   │   ├── stm32_sim.py            # Simulates STM32 sending binary data over USB# Terminal 2: Frontend│   ├── index.html     # Main HTML entry

{

  "timestamp": "2025-10-30T12:34:56.789Z",```powershell

  "system_voltage": 12.8,

  "total_current": 15.4,cd frontend│   │   ├── usb_reader.py           # Reads USB data + serves REST API

  "channels": [

    {npm run dev

      "id": 0,

      "name": "ECU",```│   │   └── requirements.txt        # Python dependencies1. **Frontend (React + Electron)** - User interface for monitoring and control

      "voltage": 12.8,

      "current": 5.2,

      "temperature": 45.3,

      "status": {**What it does:**│   │

        "on": true,

        "fault": false,- Starts React development server

        "over_current": false,

        "over_temp": false- Opens at `http://localhost:5173`│   ├── src/2. **Backend (Rust)** - API server and hardware interface  cd frontend│   └── ...            # Config files

      }

    }- Polls REST API every 500ms

  ]

}- Displays real-time dashboard with 8 channels│   │   └── main.rs                 # Reserved for future Rust implementation

```



### GET /pdm/channels

Get all channel data.---│   └── Cargo.toml                  # Rust dependencies (for future use)3. **Firmware (Arduino)** - Embedded controller for power outputs



### GET /pdm/channel/<id>

Get specific channel data (id: 0-7).

## Project Structure│

### GET /pdm/system

Get system-level data (voltage, current, active channels).



## Data Flow```├── frontend/npm install  # First time only├── backend/           # Rust backend for hardware communication



### Simulation Mode (Current)PDM/

1. **stm32_sim.py** generates realistic sensor data

2. Packs into 58-byte binary packets├── README.md                    # This file│   ├── src/                        # React components

3. Sends over virtual serial (COM10) at 10 Hz

4. **usb_reader.py** reads from paired port (COM11)├── backend/

5. Parses packets, validates checksum

6. Updates global data dictionary│   ├── Cargo.toml              # Rust dependencies (placeholder for future)│   │   ├── App.tsx                 # Main application### Data Flow

7. **Frontend** polls REST API every 500ms

8. Displays real-time dashboard│   ├── rust/                   # Rust source (placeholder for future)



### Real Hardware Mode (Future)│   │   ├── main.rs             # Reserved for future Rust backend│   │   ├── api/

1. **STM32F103** reads actual sensors

2. Packs into same 58-byte format│   │   └── lib.rs              # Reserved for future library code

3. Sends over USB serial

4. **usb_reader.py** reads from real COM port│   └── firmware/               # Python implementation (CURRENT)│   │   │   └── client.ts           # API client for backendnpm run dev│   └── src/           # Rust source code

5. Rest is identical

│       ├── stm32_sim.py       # STM32 simulator (sends data)

## Switching to Real Hardware

│       ├── usb_reader.py      # USB reader + REST API│   │   └── ...

Edit `backend/firmware/usb_reader.py`:

```python│       └── requirements.txt   # Python dependencies

# Change from:

SERIAL_PORT = "COM11"  # Virtual port└── frontend/│   ├── electron/                   # Electron desktop app```



# To:    ├── package.json           # Node dependencies

SERIAL_PORT = "COM3"   # Real STM32 port

```    ├── src/│   │   ├── main.js                 # Main process



Flash STM32 with firmware that sends same 58-byte packet format.    │   ├── App.tsx           # Main UI component



## Troubleshooting    │   ├── main.tsx          # Entry point│   │   └── preload.js              # Preload scriptFrontend                    Backend                     Hardware```└── shared/            # Shared types and protocols



**Virtual COM Ports (Windows)**    │   └── api/

1. Install [com0com](https://sourceforge.net/projects/com0com/)

2. Run Setup as Administrator    │       └── client.ts     # REST API client│   └── package.json

3. Create port pair: `install PortName=COM10 PortName=COM11`

    └── electron/

**Python Dependencies**

```powershell        ├── main.js           # Electron main process│--------                    -------                     --------

cd backend\firmware

pip install -r requirements.txt        └── preload.js        # Preload script

```

```└── README.md                       # This file

**Frontend Not Connecting**

1. Ensure `usb_reader.py` is running on port 5000

2. Check Flask output shows "Running on http://0.0.0.0:5000"

3. Verify `api/client.ts` uses `http://localhost:5000`---```React UI  <--REST/WS-->  Axum Server  <--USB Serial-->  Arduino```



## Technologies

- **Frontend**: Electron + React + TypeScript + Tailwind CSS + Vite

- **Backend**: Python (Flask) for REST API, Rust (future)## The 8 Power Channels

- **Communication**: USB Serial (binary protocol)

- **Hardware**: STM32F103 microcontroller (future)



## LicenseEach channel monitors a critical system in the race car:---                         (Rust)                         (Firmware)

MIT License



## Team

FSAE Team - Power Distribution Module Project| Ch | Name | Function | Typical Load |


|----|------|----------|--------------|

| 1 | ECU | Engine Control Unit | 5-10A |## 🚀 Quick Start                            |**Open:** http://localhost:5173  

| 2 | Fuel Pump | High-pressure fuel delivery | 8-12A |

| 3 | Ignition | Spark/coil system | 3-5A |

| 4 | Cooling Fan | Radiator cooling | 10-15A |

| 5 | Data Acquisition | Logging system | 2-4A |### Prerequisites                         Simulation

| 6 | Dashboard | Display & instruments | 1-3A |

| 7 | Sensors | Various vehicle sensors | 1-2A |

| 8 | Starter Motor | Engine cranking | 50-80A (brief) |

- **Python 3.8+** (for backend)                         (Dev Mode)**Status:** ✅ Both servers running in simulation mode!## Technologies

### Channel Data Format

- **Node.js 18+** (for frontend)

Each channel provides:

- **Voltage**: 0-16V (in volts)- **Virtual COM Port Software** (for simulation):```

- **Current**: 0-50A (in amps)

- **Temperature**: -40 to 125°C (in degrees Celsius)  - Windows: [com0com](https://sourceforge.net/projects/com0com/)

- **Status**: Object with flags:

  - `on`: Channel is active  - Linux: `socat` (built-in)

  - `fault`: General fault detected

  - `over_current`: Current limit exceeded

  - `over_temp`: Temperature limit exceeded

### Installation**Development Mode:** Backend simulates hardware (no physical device needed)  

---



## USB Communication Protocol

```powershell**Production Mode:** Backend communicates with Arduino via USB serial---- **Frontend**: Electron + React + TypeScript + Tailwind CSS + Vite

### Binary Packet Format (58 bytes)

# 1. Install Python dependencies

```

Byte  | Field              | Type    | Descriptioncd backend\firmware

------|--------------------|---------|----------------------------------

0     | Header             | uint8   | Always 0xAA (packet identifier)pip install -r requirements.txt

1-2   | CH1 Voltage        | uint16  | Millivolts (0-16000)

3-4   | CH1 Current        | uint16  | Milliamps (0-50000)## Architecture- **Backend**: Rust (for USB/CAN communication)

5-6   | CH1 Temperature    | int16   | Decidegrees C (-400 to 1250)

7     | CH1 Status         | uint8   | Bit flags (on/fault/overcurrent/overtemp)# 2. Install frontend dependencies

8-14  | CH2 Data           | 7 bytes | Same format as CH1

15-21 | CH3 Data           | 7 bytes | Same format as CH1cd ..\..\frontend

22-28 | CH4 Data           | 7 bytes | Same format as CH1

29-35 | CH5 Data           | 7 bytes | Same format as CH1npm install

36-42 | CH6 Data           | 7 bytes | Same format as CH1

43-49 | CH7 Data           | 7 bytes | Same format as CH1```### Backend Structure (Rust)## 📊 What's Running Right Now- **Build Tools**: Vite for frontend, Cargo for backend

50-56 | CH8 Data           | 7 bytes | Same format as CH1

57    | Checksum           | uint8   | XOR of all previous bytes

```

### Running the System

### Status Byte Bit Flags



```

Bit | Flag           | DescriptionYou need to run **3 terminals**:```- **Styling**: Tailwind CSS v4

----|----------------|----------------------------------

0   | ON             | Channel is powered on

1   | FAULT          | General fault condition

2   | OVER_CURRENT   | Current exceeded safe threshold#### Terminal 1: STM32 Simulator (Fake Hardware)backend/src/

3   | OVER_TEMP      | Temperature exceeded safe threshold

4-7 | Reserved       | Future use```powershell

```

cd backend\firmware├── main.rs                 # Server entry point, starts HTTP server on port 3030**Backend Server:**  

### Example Packet (Hex)

python stm32_sim.py

```

AA 0C 1C 03 E8 00 FA 01  // Header + CH1 (12.8V, 1.0A, 25.0°C, ON)```├── api/                    # HTTP REST + WebSocket endpoints

0C 1C 05 DC 00 FB 01     // CH2 (12.8V, 1.5A, 25.1°C, ON)

...**What it does:**

5A                        // Checksum

```- Simulates STM32F103 microcontroller│   ├── routes.rs          # Maps URLs to handler functions- ✅ http://127.0.0.1:3030 (REST API)## Development Setup



---- Generates realistic sensor data (voltage, current, temperature)



## REST API Endpoints- Sends binary packets over virtual COM port (COM10)│   ├── handlers/          # Processes HTTP requests, calls domain logic



Base URL: `http://localhost:5000/api`- Updates at 10 Hz (every 100ms)



### GET /health│   ├── dto/               # Request/response data structures- ✅ ws://127.0.0.1:3030/ws (WebSocket)

Health check endpoint.

#### Terminal 2: USB Reader & API Server

**Response:**

```json```powershell│   ├── middleware/        # CORS headers for cross-origin requests

{

  "status": "ok",cd backend\firmware

  "timestamp": "2025-10-30T12:34:56.789Z"

}python usb_reader.py│   └── websocket/         # Streams live data to frontend every 100ms- ✅ Simulation mode (no hardware needed)### Prerequisites

```

```

### GET /pdm/status

Get complete PDM status (all data).**What it does:**├── application/



**Response:**- Reads binary data from virtual COM port (COM11)

```json

{- Parses 58-byte packets│   └── app_state.rs       # Global state (PDM data, hardware manager, config)- ✅ 8 channels with live data- Node.js (v20+)

  "timestamp": "2025-10-30T12:34:56.789Z",

  "system_voltage": 12.8,- Stores data in memory

  "total_current": 15.4,

  "channels": [- Serves REST API on `http://localhost:5000`├── domain/

    {

      "id": 0,

      "name": "ECU",

      "voltage": 12.8,#### Terminal 3: Frontend (UI)│   ├── channel.rs         # Channel model (voltage, current, status)- Rust (latest stable)

      "current": 5.2,

      "temperature": 45.3,```powershell

      "status": {

        "on": true,cd frontend│   ├── system.rs          # System state (PdmState holds all channels)

        "fault": false,

        "over_current": false,npm run dev

        "over_temp": false

      }```│   └── hardware.rs        # Hardware message types**Frontend:**  - Git

    },

    // ... 7 more channels**What it does:**

  ]

}- Starts Vite dev server└── infrastructure/

```

- Opens Electron desktop app

### GET /pdm/channels

Get all channel data.- Makes REST API calls to `http://localhost:5000`    ├── config.rs          # Loads configuration from pdm_config.toml- ✅ http://localhost:5173



**Response:**- Displays real-time sensor data in UI

```json

{- Access web version at `http://localhost:5173`    └── hardware/

  "timestamp": "2025-10-30T12:34:56.789Z",

  "channels": [ /* array of 8 channels */ ]

}

```---        ├── manager.rs     # Switches between simulation/real hardware- ✅ Full dashboard with controls### Installation



### GET /pdm/channel/<id>

Get specific channel data (id: 0-7).

## 📊 The 8 Power Channels        ├── serial/        # USB serial protocol for Arduino communication

**Response:**

```json

{

  "timestamp": "2025-10-30T12:34:56.789Z",Each channel monitors a critical system in the race car:        └── simulation/    # Generates fake sensor data for testing- ✅ Real-time updates (simulated)

  "channel": {

    "id": 0,

    "name": "ECU",

    "voltage": 12.8,| Channel | System              | Description                          |```

    "current": 5.2,

    "temperature": 45.3,|---------|---------------------|--------------------------------------|

    "status": {

      "on": true,| 0       | ECU                 | Engine Control Unit (brain)          |1. Clone the repository

      "fault": false,

      "over_current": false,| 1       | Fuel Pump           | Fuel delivery system                 |

      "over_temp": false

    }| 2       | Ignition            | Spark/ignition system                |### Data Source Locations

  }

}| 3       | Cooling Fan         | Radiator fan (auto on/off)           |

```

| 4       | Data Acquisition    | Logging and telemetry                |---2. Install frontend dependencies:

### GET /pdm/system

Get system-level data.| 5       | Dashboard           | Driver display                       |



**Response:**| 6       | Sensors             | O2, temp, pressure sensors           |**Where data comes from:**

```json

{| 7       | Starter Motor       | High-current starter (80-120A)       |

  "timestamp": "2025-10-30T12:34:56.789Z",

  "system_voltage": 12.8,   ```bash

  "total_current": 15.4,

  "active_channels": 6### Data Per Channel

}

```1. **Simulation Mode** (`infrastructure/hardware/simulation/simulator.rs`)



---Each channel provides:



## Data Flow Explained- **Voltage**: 0-16V (in volts)   - Function `simulate_system_status()` generates random voltage/current values## 🎯 Project Overview   cd frontend



### Current Flow (Simulation Mode)- **Current**: 0-30A (0-120A for starter, in amps)



1. **stm32_sim.py** generates random but realistic sensor data- **Temperature**: 20-100°C (component temperature)   - Updates `PdmState` struct every 100ms with simulated sensor readings

2. Packs data into 58-byte binary packets

3. Sends packets over virtual serial port (COM10) at 10 Hz- **Status Flags**:

4. **usb_reader.py** reads from paired port (COM11)

5. Parses binary packets and validates checksum  - `on`: Channel is powered   - No physical hardware required   npm install

6. Updates global `pdm_data` dictionary (thread-safe)

7. **Frontend** polls REST API (`/api/pdm/status`) every 500ms  - `fault`: Fault detected

8. Displays data in real-time dashboard

  - `over_current`: Current limit exceeded

### Future Flow (Real Hardware)

  - `over_temp`: Temperature limit exceeded

1. **STM32F103** reads actual sensors (ADC, current sensors, thermistors)

2. Packs data into same 58-byte binary format2. **Real Hardware Mode** (`infrastructure/hardware/serial/port.rs`)Power Distribution Module control system with professional architecture:   ```

3. Sends over USB serial (appears as COM port)

4. **usb_reader.py** reads from real COM port (e.g., COM3)---

5. Rest of flow is identical (parse, serve API, display)

   - Reads data from Arduino via USB serial port

---

## 🔌 USB Communication Protocol

## Switching to Real Hardware

   - Parses protocol strings like "STATUS:1,12.5,2.3,ON"

When you're ready to connect real STM32 hardware:

### Binary Packet Format (58 bytes)

### Step 1: Update Serial Port

Edit `backend/firmware/usb_reader.py`:   - Updates `PdmState` struct with actual sensor values from firmware

```python

# Change from:```

SERIAL_PORT = "COM11"  # Virtual port

[Header] [Channel 0] [Channel 1] ... [Channel 7] [Checksum]### Features### Running the Application

# To:

SERIAL_PORT = "COM3"   # Real STM32 port (check Device Manager)  1 byte    7 bytes     7 bytes        7 bytes      1 byte

```

```3. **API Layer** (`api/handlers/*.rs`)

### Step 2: Flash STM32 Firmware

- Use STM32CubeIDE or PlatformIO

- Implement same 58-byte packet format

- Read sensors via ADC### Each Channel (7 bytes)   - Handlers read from `Arc<RwLock<PdmState>>` shared state- 8 independent channels (control + monitor)

- Send packets at 10 Hz over USB CDC

```

### Step 3: Stop Simulator

- You no longer need `stm32_sim.py`[Voltage] [Current] [Temperature] [Status]   - REST endpoints return current state as JSON

- Only run `usb_reader.py` and frontend

 2 bytes   2 bytes     2 bytes      1 byte

---

```   - WebSocket streams state updates in real-time- Real-time WebSocket streaming (100ms updates)1. **Start the frontend dev server:**

## Development Notes



### Python Backend

**Data encoding:**

**Dependencies:**

- `pyserial==3.5` - USB serial communication- `Voltage`: uint16 in millivolts (e.g., 13800 = 13.8V)

- `Flask==3.0.0` - REST API server

- `flask-cors==4.0.0` - CORS support for frontend- `Current`: uint16 in milliamps (e.g., 5200 = 5.2A)4. **Frontend** (`frontend/src/App.tsx`)- REST API for all operations   ```bash



**Key Files:**- `Temperature`: int16 in decidegrees Celsius (e.g., 425 = 42.5°C)

- `stm32_sim.py` - Hardware simulator

- `usb_reader.py` - Serial reader + API server- `Status`: uint8 bit flags   - **Currently:** Uses local simulated data (random numbers)



### Frontend  - Bit 0: On/Off



**Tech Stack:**  - Bit 1: Fault   - **Next step:** Will call REST API to get real backend data- Simulation mode for development   cd frontend

- React 18 with TypeScript

- Vite (build tool)  - Bit 2: Over-current

- Tailwind CSS v4

- Electron (desktop wrapper)  - Bit 3: Over-temperature   - **Next step:** Will connect WebSocket for live updates



**API Polling:**

- Polls `/api/pdm/status` every 500ms

- No WebSocket (simple REST-only architecture)**Example:**- USB serial for Arduino/custom boards   npm run dev



### Rust Backend (Future)```



Currently just placeholder files:Header: 0xAA### REST API Endpoints

- `backend/rust/main.rs` - Entry point

- `backend/rust/lib.rs` - LibraryChannel 0 (ECU):

- `backend/Cargo.toml` - Dependencies

  Voltage: 0x35E4 (13800 mV = 13.8V)- Emergency shutdown & safety features   ```

When ready to migrate to Rust:

- Implement serial communication with `serialport` crate  Current: 0x1450 (5200 mA = 5.2A)

- Use `actix-web` or `axum` for REST API

- Keep same API contract for frontend compatibility  Temp: 0x01A9 (425 = 42.5°C)```



---  Status: 0x01 (ON, no faults)



## TroubleshootingChecksum: XOR of all bytesGET  /api/health                      - Server health check



### Virtual COM Ports (Windows)```



**Error:** "Could not open serial port"GET  /api/status                      - Get all channel data



**Fix:**---

1. Install [com0com](https://sourceforge.net/projects/com0com/)

2. Run Setup Command Prompt as AdministratorPOST /api/channel/:id/control         - Turn channel on/off### Tech Stack2. **Start Electron (in another terminal):**

3. Create port pair: `install PortName=COM10 PortName=COM11`

4. Verify in Device Manager under "Ports (COM & LPT)"## 🌐 REST API Endpoints



### Python DependenciesPOST /api/emergency-shutdown          - Disable all channels



**Error:** "No module named 'serial'"The Python backend serves the following REST API endpoints:



**Fix:**POST /api/reset-all                   - Reset all to OFF- **Backend:** Rust (Axum, Tokio, WebSocket)   ```bash

```powershell

cd backend\firmware| Method | Endpoint                     | Description                      |

pip install -r requirements.txt

```|--------|------------------------------|----------------------------------|WS   /ws                              - WebSocket for live updates



### Frontend Not Connecting| GET    | `/api/health`                | Health check                     |



**Error:** "Failed to fetch system status"| GET    | `/api/pdm/status`            | Complete PDM status (all data)   |```- **Frontend:** React + TypeScript + Tailwind + Electron   cd frontend



**Fix:**| GET    | `/api/pdm/channels`          | All 8 channels data              |

1. Ensure `usb_reader.py` is running on port 5000

2. Check Flask output shows "Running on http://0.0.0.0:5000"| GET    | `/api/pdm/channel/<0-7>`     | Specific channel data            |

3. Verify frontend is using `http://localhost:5000` in `api/client.ts`

| GET    | `/api/pdm/system`            | System voltage & total current   |

---

**Example:** Control channel 1- **Hardware:** Arduino/Custom via USB Serial   npm start

## Technologies

### Example API Response

- **Frontend**: Electron + React + TypeScript + Tailwind CSS + Vite

- **Backend**: Python (Flask) for REST API, Rust (future)

- **Communication**: USB Serial (binary protocol)

- **Hardware**: STM32F103 microcontroller (future)**GET** `/api/pdm/channel/0` (ECU)



---```json```bash   ```



## License{



MIT License - See LICENSE file for details  "timestamp": "2025-10-30T14:23:45.123456",curl -X POST http://127.0.0.1:3030/api/channel/1/control \



---  "channel": {



## Team    "id": 0,  -H "Content-Type: application/json" \---



FSAE Team - Power Distribution Module Project    "name": "ECU",


    "voltage": 13.8,  -d '{"action":"on"}'

    "current": 5.2,

    "temperature": 45.0,```3. **For backend development (when implemented):**

    "status": {

      "on": true,

      "fault": false,

      "over_current": false,### USB Serial Protocol## 📁 Structure   ```bash

      "over_temp": false

    }

  }

}Commands sent from backend to Arduino:   cd backend

```



---

``````   cargo run

## 🔄 Data Flow Explained

SET:CH1:ON\n        # Turn channel 1 on

### 1. **Data Generation** (stm32_sim.py)

- Simulates realistic sensor valuesSET:CH1:OFF\n       # Turn channel 1 offPDM/   ```

- Packs data into 58-byte binary packets

- Sends to virtual COM10 at 115200 baud, 10 HzGET:STATUS\n        # Request full status



### 2. **Data Reading** (usb_reader.py)EMERGENCY:STOP\n    # Shutdown all channels├── backend/              # Rust server

- Reads from virtual COM11

- Validates packet (header + checksum)```

- Unpacks binary data into readable values

- Stores in memory (thread-safe)│   ├── api/             # REST + WebSocket## Project Structure



### 3. **Data Serving** (usb_reader.py)Responses sent from Arduino to backend:

- Flask server runs on port 5000

- REST API endpoints query in-memory data│   ├── domain/          # Business logic

- CORS enabled for frontend access

```

### 4. **Data Display** (frontend)

- React app makes HTTP GET requestsACK:command\n                    # Command received│   └── infrastructure/  # Hardware layer### Frontend (`frontend/`)

- Fetches data every 100-500ms

- Updates UI with real-time valuesSTATUS:ch,voltage,current,state  # Channel data

- Displays graphs, gauges, status indicators

SYSTEM:Vin,Itotal,temp           # System metrics├── frontend/            # React + Electron UI- `electron/` - Electron main process and preload scripts

---

ERROR:message                    # Error occurred

## 🔧 Switching to Real Hardware

```└── firmware/            # Arduino examples- `src/` - React application source

When the actual STM32F103 is ready:



1. **Stop the simulator**

   ```powershell## Configuration    ├── simulated/       # Example code  - `components/` - Reusable UI components

   # Press Ctrl+C in Terminal 1 (stm32_sim.py)

   ```



2. **Update COM port in usb_reader.py**Edit `backend/pdm_config.toml`:    └── real-hardware/   # Your firmware  - `pages/` - Application pages/views

   ```python

   # Line 13 in usb_reader.py

   SERIAL_PORT = "COM3"  # Change to actual STM32 port

   ``````toml```  - `App.tsx` - Main application component



3. **Restart usb_reader.py**[hardware]

   ```powershell

   python usb_reader.pysimulation_mode = true           # Set false for real hardware  - `main.tsx` - React entry point

   ```

serial_port = "COM3"            # Arduino port (Windows)

4. **Done!** The rest of the system stays the same.

serial_baud_rate = 115200See `FILE_STRUCTURE_GUIDE.md` for details.- `index.html` - Main HTML file

---

auto_detect_arduino = true

## 🛠️ Development Notes

- Configuration files for Vite, Tailwind, PostCSS, etc.

### Current Implementation

- **Backend**: Python (Flask + PySerial)[safety]

- **Frontend**: React + TypeScript + Vite + Electron

- **Communication**: USB Serial (binary protocol)max_total_current = 60.0---



### Future Rust Backendmax_channel_current = 15.0

The `backend/src/main.rs` file is reserved for a future Rust implementation. When ready:

- Use `axum` or `actix-web` for REST APImax_temperature = 80.0### Backend (`backend/`)

- Use `serialport` crate for USB communication

- Replace Python backend entirelymin_input_voltage = 10.0



---max_input_voltage = 16.0## 🔌 API Quick Reference- `src/` - Rust source code for hardware communication



## 📝 Troubleshooting



### Virtual COM ports not working[system]- Will handle USB and CAN bus communication



**Windows:**update_interval_ms = 100

1. Install [com0com](https://sourceforge.net/projects/com0com/)

2. Create pair: COM10 <-> COM11num_channels = 8### REST Endpoints

3. Update port names in scripts if needed

```

**Linux:**

```bash### Shared (`shared/`)

socat -d -d pty,raw,echo=0 pty,raw,echo=0

# Note the /dev/pts/X devices created, update scripts## Hardware Integration

```

```bash- Common types and protocols used by both frontend and backend

### "Port already in use"

- Make sure only one instance of each script is running### Using Real Arduino

- Check Windows Device Manager for port conflicts

# Health

### No data in frontend

- Verify all 3 terminals are running1. **Flash firmware** to Arduino:

- Check browser console for API errors

- Test API manually: `http://localhost:5000/api/health`   - Open `firmware/simulated/arduino_example.ino` in Arduino IDEGET http://127.0.0.1:3030/api/health## Scripts



---   - Upload to board



## 📄 License



This project is for FSAE team use.2. **Configure backend**:



---   - Set `simulation_mode = false` in `pdm_config.toml`# System status### Frontend



## 👥 Team   - Set correct `serial_port` (check Device Manager)



Built for Formula SAE competition by [Your Team Name]GET http://127.0.0.1:3030/api/status- `npm run dev` - Start Vite dev server



---3. **Restart backend**:



**Status:** ✅ Simulation Mode Active | Ready for Real Hardware Integration   ```bash- `npm run build` - Build for production


   cd backend

   cargo run# Control channel- `npm start` - Start Electron app

   ```

POST http://127.0.0.1:3030/api/channel/1/control

Backend will auto-detect Arduino and begin USB communication.

{"action": "on"}### Backend (when implemented)

## Development

- `cargo run` - Run in development

### Backend

# Emergency stop- `cargo build --release` - Build for production

```bash

cd backendPOST http://127.0.0.1:3030/api/emergency-shutdown

cargo run          # Start server

cargo test         # Run tests```## Contributing

cargo build --release  # Production build

```



### Frontend### WebSocket1. Keep frontend and backend code in their respective directories



```bash2. Use TypeScript for frontend code

cd frontend

npm run dev        # Development server```javascript3. Use Tailwind for styling

npm run build      # Production build

npm run electron   # Run as desktop appconst ws = new WebSocket('ws://127.0.0.1:3030/ws');4. Add proper type definitions for shared interfaces

```

// Receives system status every 100ms

## Project Structure

```## Production Build

```

PDM/

├── backend/                # Rust API server

├── frontend/               # React UI---1. Build frontend: `cd frontend && npm run build`

├── firmware/               # Arduino code examples

│   ├── simulated/         # Example with protocol implementation2. Build backend: `cd backend && cargo build --release`

│   └── real-hardware/     # Place your production code here

└── README.md              # This file## 🔧 Hardware Integration3. Package Electron app (configuration TBD)

```



## Safety Notes### Now: Simulation Mode ✅

```

This system controls high-current electrical loads. Before using with real hardware:Frontend ← → Backend (Simulation)

```

- Test thoroughly in simulation modeNo hardware needed - perfect for development!

- Verify emergency shutdown works

- Use appropriate fuses and wire gauge### Later: Real Hardware

- Implement hardware overcurrent protection```

- Never exceed component current ratingsFrontend ← → Backend ← → Arduino ← → MOSFETs ← → Loads

- Always have fire suppression available```



## Technical Details**To switch:**

1. Flash `firmware/simulated/arduino_example.ino` to Arduino

**Backend:** Rust 1.70+, Axum 0.7, Tokio async runtime, serialport  2. Edit `backend/pdm_config.toml`: `simulation_mode = false`

**Frontend:** Node.js 18+, React 19, TypeScript, Tailwind CSS, Electron  3. Restart backend

**Protocol:** Text-based serial (115200 baud)  

**Update Rate:** 100ms (10Hz)See `firmware/README.md` for complete guide.



## Next Steps---



1. Connect frontend to backend API (replace simulated data)## 📚 Documentation

2. Implement WebSocket client for real-time updates

3. Test with physical Arduino hardware| File | Description |

4. Add data logging functionality|------|-------------|

| `README.md` | This quick start guide |
| `PROJECT_STATUS.md` | Detailed status & next steps |
| `FILE_STRUCTURE_GUIDE.md` | Architecture explanation |
| `firmware/README.md` | Hardware integration guide |
| `firmware/simulated/arduino_example.ino` | Complete Arduino example |

---

## 🏗️ Architecture

**Layered Backend:**
```
API Layer → Application → Domain → Infrastructure
```

**Why?**
- Easy to test (mock hardware)
- Easy to swap (simulation ↔ real)
- Professional maintainability
- Fortune 500 standards

---

## 🧪 Development

### Backend
```bash
cd backend
cargo run        # Run server
cargo test       # Tests
cargo clippy     # Lint
```

### Frontend
```bash
cd frontend
npm run dev      # Dev server
npm run build    # Production build
```

---

## ✅ Current Status

**Completed:**
- ✅ Backend fully functional
- ✅ REST API working
- ✅ WebSocket streaming
- ✅ Simulation mode
- ✅ Frontend UI complete
- ✅ Firmware examples ready
- ✅ Documentation complete

**Next:**
- ⏳ Connect frontend to backend API
- ⏳ Replace simulated data with real calls
- ⏳ Test with Arduino hardware

See `PROJECT_STATUS.md` for details.

---

## 🚨 Safety

⚠️ **This controls high-current loads!**

**Safety features:**
- Emergency shutdown
- Input validation
- Fault detection
- Overcurrent protection (hardware)

**Before real hardware:**
1. Test in simulation
2. Verify safety features
3. Use proper fuses
4. Start with low-current loads
5. Have fire extinguisher ready

---

## 📦 Building

```bash
# Backend release
cd backend
cargo build --release

# Frontend Electron
cd frontend
npm run electron:build
```

---

## 🎓 Learning Resources

This project demonstrates:
- Clean architecture
- Real-time systems
- Hardware abstraction
- Safety-critical design
- Full-stack development
- USB serial protocols

**For students:** The firmware structure makes it easy to go from simulation to real hardware!

---

## 🤝 Contributing

Educational project - contributions welcome!

1. Fork repo
2. Create feature branch
3. Test in simulation
4. Submit PR

---

## 📞 Need Help?

- Setup: Check `PROJECT_STATUS.md`
- Hardware: See `firmware/README.md`  
- API: Review endpoints above
- Firmware: Study `arduino_example.ino`

---

**Built with:** Rust 🦀 | React ⚛️ | TypeScript 📘 | Electron 🖥️  
**Status:** ✅ Backend Complete | ⏳ Frontend Integration Next  
**License:** [Add your license]

**Happy building! 🏁⚡**
