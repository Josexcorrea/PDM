# PDM Project - File Structure Guide

## 📁 Project Overview
```
pdm/
├── backend/           # Rust server for hardware communication
├── frontend/          # React desktop application
├── .gitignore        # Git ignore rules
├── README.md         # Project documentation
└── PROJECT_DEMO_SCRIPT.md  # 20-second demo script
```

## 🦀 Backend (Rust)
```
backend/
├── Cargo.toml        # Rust dependencies and project config
└── src/
    └── main.rs       # Main Rust server (USB/CAN communication)
```

## ⚛️ Frontend (React + Electron)
```
frontend/
├── package.json      # Node.js dependencies and scripts
├── package-lock.json # Locked dependency versions
├── index.html        # Main HTML entry point
├── vite.config.ts    # Vite build configuration
├── tailwind.config.js # Tailwind CSS styling config
├── postcss.config.js  # PostCSS processing config
├── electron/         # Electron desktop wrapper
│   ├── main.js       # Electron main process
│   └── preload.js    # Electron security bridge
└── src/              # React application source
    ├── main.tsx      # React entry point
    ├── App.tsx       # Main PDM dashboard component
    └── index.css     # Global styles (Tailwind)
```

## 📄 File Purposes:

### Configuration Files:
- **Cargo.toml** - Rust project settings and dependencies
- **package.json** - Frontend dependencies and build scripts
- **vite.config.ts** - Build tool configuration
- **tailwind.config.js** - CSS framework setup
- **postcss.config.js** - CSS processing pipeline

### Application Files:
- **main.rs** - Rust backend server (handles hardware)
- **main.tsx** - React app initialization
- **App.tsx** - Main PDM dashboard interface
- **index.html** - HTML shell for the app

### Electron Files:
- **main.js** - Creates desktop window
- **preload.js** - Security layer for frontend-backend communication

### Documentation:
- **README.md** - Setup and usage instructions
- **.gitignore** - Files to exclude from Git
- **PROJECT_DEMO_SCRIPT.md** - Demo presentation guide
