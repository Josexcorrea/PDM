// PostCSS configuration - processes CSS files during build
module.exports = {
  // Plugins that transform CSS during the build process
  plugins: {
    tailwindcss: {},             // Process Tailwind CSS v3 directives (@tailwind base, etc.)
    autoprefixer: {},            // Add vendor prefixes for browser compatibility
  },
};
