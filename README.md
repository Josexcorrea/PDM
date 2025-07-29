# PDM Desktop Application

A Power Distribution Module (PDM) desktop application built with Electron, React, and Rust for hardware communication.

## Architecture

```
pdm/
├── frontend/           # Electron + React frontend
│   ├── electron/       # Electron main process
│   ├── src/           # React source code
│   ├── index.html     # Main HTML entry
│   └── ...            # Config files
├── backend/           # Rust backend for hardware communication
│   └── src/           # Rust source code
└── shared/            # Shared types and protocols
```

## Technologies

- **Frontend**: Electron + React + TypeScript + Tailwind CSS + Vite
- **Backend**: Rust (for USB/CAN communication)
- **Build Tools**: Vite for frontend, Cargo for backend
- **Styling**: Tailwind CSS v4

## Development Setup

### Prerequisites
- Node.js (v20+)
- Rust (latest stable)
- Git

### Installation

1. Clone the repository
2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the frontend dev server:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Start Electron (in another terminal):**
   ```bash
   cd frontend
   npm start
   ```

3. **For backend development (when implemented):**
   ```bash
   cd backend
   cargo run
   ```

## Project Structure

### Frontend (`frontend/`)
- `electron/` - Electron main process and preload scripts
- `src/` - React application source
  - `components/` - Reusable UI components
  - `pages/` - Application pages/views
  - `App.tsx` - Main application component
  - `main.tsx` - React entry point
- `index.html` - Main HTML file
- Configuration files for Vite, Tailwind, PostCSS, etc.

### Backend (`backend/`)
- `src/` - Rust source code for hardware communication
- Will handle USB and CAN bus communication

### Shared (`shared/`)
- Common types and protocols used by both frontend and backend

## Scripts

### Frontend
- `npm run dev` - Start Vite dev server
- `npm run build` - Build for production
- `npm start` - Start Electron app

### Backend (when implemented)
- `cargo run` - Run in development
- `cargo build --release` - Build for production

## Contributing

1. Keep frontend and backend code in their respective directories
2. Use TypeScript for frontend code
3. Follow React and Rust best practices
4. Use Tailwind for styling
5. Add proper type definitions for shared interfaces

## Production Build

1. Build frontend: `cd frontend && npm run build`
2. Build backend: `cd backend && cargo build --release`
3. Package Electron app (configuration TBD)
