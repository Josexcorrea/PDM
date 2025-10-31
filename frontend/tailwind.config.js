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
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      {
        fiu: {
          primary: "#081E3F",    // FIU Blue
          secondary: "#B6862C",  // FIU Gold
          accent: "#F0B429",     // Lighter gold accent
          neutral: "#1F2937",    // Slate/neutral
          "base-100": "#FFFFFF",
          "base-200": "#F3F4F6",
          "base-300": "#E5E7EB",
          info: "#2563EB",
          success: "#16A34A",
          warning: "#F59E0B",
          error: "#DC2626",
        },
      },
      {
        "fiu-dark": {
          primary: "#B6862C",     // Gold as primary in dark mode for contrast
          secondary: "#081E3F",   // Deep blue secondary backgrounds
          accent: "#F0B429",
          neutral: "#111827",
          "base-100": "#0B1220", // deep navy background
          "base-200": "#0F172A",
          "base-300": "#1F2937",
          "base-content": "#FFFFFF", // force pure white text for high contrast
          info: "#60A5FA",
          success: "#22C55E",
          warning: "#FBBF24",
          error: "#F87171",
        },
      },
      "corporate", // light default
      "business",  // dark elegant
      "emerald",
      "synthwave",
      "night",
    ],
    base: true,
    styled: true,
    logs: false,
  },
};
