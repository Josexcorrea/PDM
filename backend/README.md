# PDM Backend Server

A high-performance Rust backend for the Power Distribution Module (PDM) desktop application. Handles hardware communication, real-time monitoring, and provides HTTP APIs for the frontend.

## 🚀 Features

- **Real-time Hardware Communication**: USB/Serial and CAN bus support
- **HTTP API Server**: RESTful endpoints for frontend integration
- **Safety Systems**: Emergency shutdown, fault detection, current limiting
- **Simulation Mode**: Development without physical hardware
- **Async Architecture**: High-performance concurrent processing
- **Configuration Management**: TOML-based configuration system
- **Comprehensive Logging**: Structured logging with tracing

## 🏗️ Architecture

```
PDM Backend
├── API Layer (HTTP/REST)
├── Hardware Abstraction Layer
├── Safety & Monitoring Systems
├── Configuration Management
└── Data Models & State Management
```

## 📦 Dependencies

### Core Dependencies
- **tokio**: Async runtime for concurrent operations
- **axum**: Modern HTTP server framework
- **serde**: Serialization/deserialization
- **tracing**: Structured logging

### Hardware Communication
- **serialport**: USB/Serial communication
- **socketcan**: CAN bus communication (Linux)

### Configuration & Utilities
- **toml**: Configuration file parsing
- **chrono**: Date/time handling
- **anyhow**: Error handling

## 🛠️ Development Setup

### Prerequisites
- Rust 1.70+ (latest stable recommended)
- Cargo package manager

### Installation
```bash
# Clone the repository (if not already done)
cd backend

# Install dependencies
cargo build

# Run in development mode (simulation)
cargo run

# Run with logging
RUST_LOG=debug cargo run
```

## 🔧 Configuration

The backend uses `pdm_config.toml` for configuration. On first run, a default config will be created:

```toml
# Server settings
server_address = "127.0.0.1:3030"
api_version = "1.0.0"

[hardware]
# Hardware communication settings
serial_port = null          # Auto-detect
serial_baud_rate = 115200
can_interface = "can0"
can_bitrate = 500000
status_update_interval_ms = 100
monitoring_interval_ms = 50
simulation_mode = true      # Set to false for real hardware

[safety]
# Safety limits and thresholds
max_input_voltage = 16.0
min_input_voltage = 10.0
max_total_current = 100.0
max_temperature = 85.0
default_channel_current_limit = 15.0
emergency_shutdown_timeout = 5

[logging]
# Logging configuration
level = "info"
log_to_file = true
log_file_path = "pdm_backend.log"
```

## 🌐 API Endpoints

### System Status
- `GET /api/health` - Health check
- `GET /api/status` - Current PDM status and all channel data
- `GET /api/config` - System configuration

### Channel Control
- `POST /api/channel/{id}/control` - Control specific channel
- `POST /api/channel/{id}/toggle` - Toggle channel on/off

### Emergency Controls
- `POST /api/emergency-shutdown` - Emergency shutdown all channels
- `POST /api/reset-all` - Reset all channels to OFF

### Example API Usage

```bash
# Get system status
curl http://localhost:3030/api/status

# Turn on channel 1
curl -X POST http://localhost:3030/api/channel/1/control \
  -H "Content-Type: application/json" \
  -d '{"channel": 1, "action": "TurnOn"}'

# Emergency shutdown
curl -X POST http://localhost:3030/api/emergency-shutdown \
  -H "Content-Type: application/json" \
  -d '{"reason": "Safety test"}'
```

## 🧪 Testing

```bash
# Run all tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test
cargo test test_channel_control

# Run with logging
RUST_LOG=debug cargo test
```

## 🚀 Production Build

```bash
# Build optimized release binary
cargo build --release

# The binary will be in target/release/pdm-backend
./target/release/pdm-backend
```

## 🔍 Hardware Integration

### USB/Serial Communication
The backend supports communication with PDM hardware over USB/Serial:

1. **Auto-detection**: Automatically finds PDM device
2. **Protocol handling**: Implements PDM communication protocol
3. **Error recovery**: Handles connection loss and recovery

### CAN Bus Communication
For automotive applications with CAN bus:

1. **Linux SocketCAN**: Uses standard Linux CAN interface
2. **Message filtering**: Filters relevant PDM messages
3. **Real-time performance**: Low-latency communication

### Simulation Mode
For development without hardware:
- Realistic data simulation
- All API endpoints work normally
- Configurable simulation parameters

## 📊 Monitoring & Logging

### Structured Logging
```rust
tracing::info!("Channel {} enabled", channel_id);
tracing::warn!("High temperature detected: {}°C", temp);
tracing::error!("Hardware communication failed: {}", error);
```

### Metrics & Monitoring
- Real-time channel status
- System health monitoring
- Performance metrics
- Hardware fault detection

## 🛡️ Safety Features

### Emergency Systems
- **Emergency Shutdown**: Immediate power cut to all channels
- **Overcurrent Protection**: Per-channel current limiting
- **Temperature Monitoring**: Thermal shutdown protection
- **Voltage Monitoring**: Under/overvoltage protection

### Fault Detection
- Hardware communication timeouts
- Channel fault detection
- System status monitoring
- Automatic recovery procedures

## 🧩 Module Structure

```
src/
├── main.rs           # Application entry point
├── api.rs            # HTTP API endpoints
├── hardware.rs       # Hardware communication layer
├── models.rs         # Data structures and types
└── config.rs         # Configuration management
```

### Key Components

- **`main.rs`**: Application bootstrap, server setup
- **`api.rs`**: REST API endpoints and handlers
- **`hardware.rs`**: Hardware abstraction and communication
- **`models.rs`**: Data models, state management
- **`config.rs`**: Configuration loading and management

## 🔄 Integration with Frontend

The backend provides seamless integration with the React/Electron frontend:

1. **HTTP API**: RESTful endpoints for all operations
2. **Real-time Updates**: Continuous data streaming
3. **CORS Support**: Cross-origin requests enabled
4. **Error Handling**: Proper HTTP status codes and error messages

## 📈 Performance

- **Async Architecture**: Non-blocking I/O operations
- **Low Latency**: Sub-100ms response times
- **High Throughput**: Handles multiple concurrent requests
- **Resource Efficient**: Minimal memory and CPU usage

## 🐛 Troubleshooting

### Common Issues

1. **Hardware Not Found**
   - Check USB connection
   - Verify device permissions
   - Enable simulation mode for testing

2. **CAN Bus Errors**
   - Check CAN interface configuration
   - Verify bitrate settings
   - Ensure proper CAN bus termination

3. **API Connection Issues**
   - Check server address configuration
   - Verify firewall settings
   - Ensure port is not in use

### Debug Mode
```bash
RUST_LOG=debug cargo run
```

## 🤝 Contributing

1. Follow Rust best practices
2. Add tests for new features
3. Update documentation
4. Use conventional commit messages

## 📄 License

This project is part of the PDM Desktop Application suite.
