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




