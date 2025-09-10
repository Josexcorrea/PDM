@echo off
REM PDM Backend Build and Run Script for Windows

echo 🦀 PDM Backend Build Script
echo =========================

REM Check if Rust is installed
where cargo >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Rust/Cargo not found. Please install Rust first:
    echo    https://rustup.rs/
    exit /b 1
)

echo ✅ Rust/Cargo found

REM Check current directory
if not exist "Cargo.toml" (
    echo ❌ Cargo.toml not found. Please run this script from the backend directory.
    exit /b 1
)

echo 📦 Installing dependencies...
cargo check
if %ERRORLEVEL% neq 0 (
    echo ❌ Dependency check failed
    exit /b 1
)

echo 🔧 Building project...
cargo build
if %ERRORLEVEL% neq 0 (
    echo ❌ Build failed
    exit /b 1
)

echo 🧪 Running tests...
cargo test
if %ERRORLEVEL% neq 0 (
    echo ⚠️  Some tests failed, but continuing...
)

echo.
echo 🚀 Build completed successfully!
echo.
echo To run the backend server:
echo   cargo run                    # Normal mode
echo   set RUST_LOG=debug ^&^& cargo run     # Debug mode
echo   cargo run --release          # Release mode
echo.
echo The server will start on http://127.0.0.1:3030
echo API documentation available in README.md

pause
