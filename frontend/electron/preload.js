// Preload script - runs before the web page loads and can safely expose APIs
// This script runs in a secure context between the main process and renderer

// Wait for the HTML document to finish loading
window.addEventListener('DOMContentLoaded', () => {
  // You can expose APIs to the renderer here if needed
  // Example: window.electronAPI = { someFunction: () => {} }
});
