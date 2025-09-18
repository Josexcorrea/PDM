
// Import error handling type from anyhow crate
use anyhow::Result;
// Import logging macros from tracing crate
use tracing::{info, error};
// Import thread-safe reference counting pointer
use std::sync::Arc;
// Import async read/write lock for shared state
use tokio::sync::RwLock;

// Declare submodules for API, hardware, models, and config
mod api;
mod hardware;
mod models;
mod config;

// Import PdmState struct from models module
use models::PdmState;
// Import HardwareManager struct from hardware module
use hardware::HardwareManager;
// Import create_router function from api module
use api::create_router;

// Main async entry point for the backend server
#[tokio::main] // Macro to use Tokio runtime for async main
async fn main() -> Result<()> { // Main function, returns Result for error handling
    // Initialize logging system
    tracing_subscriber::fmt::init();
    
    // Log server startup
    info!("PDM Backend Server starting...");
    
    // Load configuration from file or environment
    let config = config::Config::load()?;
    // Log loaded configuration
    info!("Configuration loaded: listening on {}", config.server_address);
    
    // Create shared, thread-safe PdmState
    let pdm_state = Arc::new(RwLock::new(PdmState::new()));
    
    // Create shared, thread-safe HardwareManager
    let hardware_manager = Arc::new(HardwareManager::new(config.clone())?);
    
    // Start hardware monitoring in a background task
    let hardware_task = {
        let pdm_state = Arc::clone(&pdm_state); // Clone Arc for task
        let hardware_manager = Arc::clone(&hardware_manager); // Clone Arc for task
        
        // Spawn async task for hardware monitoring
        tokio::spawn(async move {
            if let Err(e) = hardware_manager.start_monitoring(pdm_state).await {
                // Log error if monitoring fails
                error!("Hardware monitoring failed: {}", e);
            }
        })
    };
    
    // Create API router with shared state
    let app = create_router(pdm_state, hardware_manager);
    
    // Bind TCP listener to server address
    let listener = tokio::net::TcpListener::bind(&config.server_address).await?;
    // Log API server address
    info!("PDM API server listening on {}", config.server_address);
    // Log backend readiness
    info!("Backend ready for frontend connections");
    
    // Start HTTP server in a background task
    let server_task = tokio::spawn(async move {
        if let Err(e) = axum::serve(listener, app).await {
            // Log error if server fails
            error!("Server error: {}", e);
        }
    });
    
    // Wait for hardware or server task to finish, or for shutdown signal
    tokio::select! {
        _ = hardware_task => {
            // Log if hardware task ends unexpectedly
            error!("Hardware monitoring task ended unexpectedly");
        }
        _ = server_task => {
            // Log if server task ends unexpectedly
            error!("Server task ended unexpectedly");
        }
        _ = tokio::signal::ctrl_c() => {
            // Log shutdown signal
            info!("Shutdown signal received");
        }
    }
    
    // Log server shutdown
    info!("PDM Backend Server shutting down");
    Ok(()) // Return success
}
