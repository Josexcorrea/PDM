// Import Vite configuration function and React plugin
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Export Vite configuration for the frontend build process
export default defineConfig({
  // Plugins - add React support to Vite
  plugins: [react()],
  // Set base path so Electron can load assets correctly in production
  base: './', 
  // Development server configuration
  server: {
    port: 5173,
  },
});

