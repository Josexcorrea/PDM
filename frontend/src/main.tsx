// Import React library for creating components
import React from 'react';
// Import createRoot function to mount the React app to the DOM
import { createRoot } from 'react-dom/client';
// Import the main App component
import App from './App';
// Import global CSS styles (includes Tailwind)
import './index.css';

/**
 * React Application Entry Point
 * 
 * This file initializes the React application and mounts it to the DOM.
 * It's loaded by Vite and rendered inside the Electron window.
 */

// Find the HTML element where React will render the app
const rootElement = document.getElementById('root');

// Check if the root element exists, throw error if not found
if (!rootElement) {
  throw new Error('Failed to find the root element. Make sure index.html has a div with id="root"');
}

// Create React root and render the App component inside it
const root = createRoot(rootElement);
// Start the React application by rendering the App component
root.render(<App />);
