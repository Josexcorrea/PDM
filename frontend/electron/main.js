// Import Electron modules for creating desktop app windows
const { app, BrowserWindow } = require('electron');
// Import path module for handling file paths
const path = require('path');

// Check if app is running in development mode (not packaged)
const isDev = !app.isPackaged;

// Function to create the main application window
function createWindow() {
  // Create a new browser window with specific settings
  const win = new BrowserWindow({
    width: 1200,    // Window width in pixels
    height: 800,    // Window height in pixels
    webPreferences: {
      nodeIntegration: false,     // Disable Node.js in renderer for security
      contextIsolation: true,     // Enable context isolation for security
      preload: path.join(__dirname, 'preload.js'),  // Load preload script
    },
  });

  // Load content based on development or production mode
  if (isDev) {
    // In development: load from Vite dev server
    win.loadURL('http://localhost:5173'); // Vite dev server
    //win.webContents.openDevTools();      // Uncomment to auto-open dev tools
  } else {
    // In production: load from built files
    win.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

// Create window when Electron is ready
app.whenReady().then(createWindow);

// Quit app when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
