/**
 * Tailwind CSS v3 Configuration for PDM Desktop Application
 */

// Export Tailwind v3 configuration object - uses CommonJS
module.exports = {
  // Tell Tailwind which files to scan for CSS classes
  content: [
    "./src/**/*.{html,js,jsx,ts,tsx}",  // All source files
    "./index.html"                       // Main HTML file
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
