/**
 * PDM Backend Server
 * 
 * This is the main entry point for the PDM backend server.
 * It handles hardware communication and provides APIs for the frontend.
 * 
 * Architecture:
 * - HTTP API server for frontend communication
 * - Hardware abstraction layer for PDM communication
 * - Real-time channel monitoring and control
 * - Safety systems and fault detection
 */

use anyhow::Result;
use tracing::{info, error};
use std::sync::Arc;
use tokio::sync::RwLock;

// Import our modules
mod api;
mod hardware;
mod models;
mod config;

use models::PdmState;
use hardware::HardwareManager;
use api::create_router;

// Main entry point - sets up and runs the backend server
#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::fmt::init();
    
    info!("🚀 PDM Backend Server starting...");
    
    // Load configuration
    let config = config::Config::load()?;
    info!("📋 Configuration loaded: listening on {}", config.server_address);
    
    // Initialize shared PDM state
    let pdm_state = Arc::new(RwLock::new(PdmState::new()));
    
    // Initialize hardware manager
    let hardware_manager = Arc::new(HardwareManager::new(config.clone())?);
    
    // Start hardware monitoring task
    let hardware_task = {
        let pdm_state = Arc::clone(&pdm_state);
        let hardware_manager = Arc::clone(&hardware_manager);
        
        tokio::spawn(async move {
            if let Err(e) = hardware_manager.start_monitoring(pdm_state).await {
                error!("Hardware monitoring failed: {}", e);
            }
        })
    };
    
    // Create API router with shared state
    let app = create_router(pdm_state, hardware_manager);
    
    // Start the HTTP server
    let listener = tokio::net::TcpListener::bind(&config.server_address).await?;
    info!("🌐 PDM API server listening on {}", config.server_address);
    info!("✅ Backend ready for frontend connections");
    
    // Run the server
    let server_task = tokio::spawn(async move {
        if let Err(e) = axum::serve(listener, app).await {
            error!("Server error: {}", e);
        }
    });
    
    // Wait for either task to complete (or fail)
    tokio::select! {
        _ = hardware_task => {
            error!("Hardware monitoring task ended unexpectedly");
        }
        _ = server_task => {
            error!("Server task ended unexpectedly");
        }
        _ = tokio::signal::ctrl_c() => {
            info!("🛑 Shutdown signal received");
        }
    }
    
    info!("👋 PDM Backend Server shutting down");
    Ok(())
}
