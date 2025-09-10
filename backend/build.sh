#!/bin/bash

# PDM Backend Build and Run Script

echo "🦀 PDM Backend Build Script"
echo "========================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Rust is installed
if ! command_exists cargo; then
    echo "❌ Rust/Cargo not found. Please install Rust first:"
    echo "   https://rustup.rs/"
    exit 1
fi

echo "✅ Rust/Cargo found"

# Check current directory
if [ ! -f "Cargo.toml" ]; then
    echo "❌ Cargo.toml not found. Please run this script from the backend directory."
    exit 1
fi

echo "📦 Installing dependencies..."
cargo check

if [ $? -ne 0 ]; then
    echo "❌ Dependency check failed"
    exit 1
fi

echo "🔧 Building project..."
cargo build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "🧪 Running tests..."
cargo test

if [ $? -ne 0 ]; then
    echo "⚠️  Some tests failed, but continuing..."
fi

echo ""
echo "🚀 Build completed successfully!"
echo ""
echo "To run the backend server:"
echo "  cargo run                    # Normal mode"
echo "  RUST_LOG=debug cargo run     # Debug mode"
echo "  cargo run --release          # Release mode"
echo ""
echo "The server will start on http://127.0.0.1:3030"
echo "API documentation available in README.md"
