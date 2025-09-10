/**
 * HTTP API Server for PDM Backend
 * 
 * This module provides REST API endpoints for frontend communication:
 * - GET /api/status - Get current PDM status
 * - POST /api/channel/{id}/control - Control individual channels
 * - POST /api/emergency-shutdown - Emergency shutdown all channels
 * - GET /api/health - Health check endpoint
 * - WebSocket endpoint for real-time updates (future)
 */

use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde_json::{json, Value};
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{info, error};
use tower_http::cors::CorsLayer;

use crate::models::{PdmState, ChannelControlRequest, EmergencyShutdownRequest, SystemStatusResponse, ChannelStatus};
use crate::hardware::HardwareManager;

/// Application state shared between API handlers
#[derive(Clone)]
pub struct AppState {
    pub pdm_state: Arc<RwLock<PdmState>>,
    pub hardware_manager: Arc<HardwareManager>,
    pub startup_time: std::time::Instant,
}

/// Create the API router with all endpoints
pub fn create_router(
    pdm_state: Arc<RwLock<PdmState>>,
    hardware_manager: Arc<HardwareManager>,
) -> Router {
    let app_state = AppState {
        pdm_state,
        hardware_manager,
        startup_time: std::time::Instant::now(),
    };
    
    Router::new()
        // Health check endpoint
        .route("/api/health", get(health_check))
        
        // System status endpoint
        .route("/api/status", get(get_system_status))
        
        // Channel control endpoints
        .route("/api/channel/:id/control", post(control_channel))
        .route("/api/channel/:id/toggle", post(toggle_channel))
        
        // Emergency controls
        .route("/api/emergency-shutdown", post(emergency_shutdown))
        .route("/api/reset-all", post(reset_all_channels))
        
        // Configuration endpoints
        .route("/api/config", get(get_config))
        
        // Add CORS middleware for frontend communication
        .layer(CorsLayer::permissive())
        .with_state(app_state)
}

/// Health check endpoint - returns basic server status
async fn health_check(State(state): State<AppState>) -> Result<Json<Value>, StatusCode> {
    let uptime = state.startup_time.elapsed().as_secs();
    
    Ok(Json(json!({
        "status": "healthy",
        "service": "pdm-backend",
        "version": "1.0.0",
        "uptime_seconds": uptime,
        "timestamp": chrono::Utc::now()
    })))
}

/// Get current PDM system status
async fn get_system_status(State(state): State<AppState>) -> Result<Json<SystemStatusResponse>, StatusCode> {
    let pdm_state = state.pdm_state.read().await;
    let uptime = state.startup_time.elapsed().as_secs();
    
    let response = SystemStatusResponse {
        pdm_state: pdm_state.clone(),
        uptime_seconds: uptime,
        api_version: "1.0.0".to_string(),
    };
    
    Ok(Json(response))
}

/// Control a specific channel (turn on/off, set limits)
async fn control_channel(
    Path(channel_id): Path<u8>,
    State(state): State<AppState>,
    Json(request): Json<ChannelControlRequest>,
) -> Result<Json<Value>, StatusCode> {
    if channel_id < 1 || channel_id > 8 {
        return Err(StatusCode::BAD_REQUEST);
    }
    
    info!("Channel {} control request: {:?}", channel_id, request.action);
    
    // Determine the target state based on action
    let enable = match request.action {
        crate::models::ChannelAction::TurnOn => true,
        crate::models::ChannelAction::TurnOff => false,
        crate::models::ChannelAction::Toggle => {
            let pdm_state = state.pdm_state.read().await;
            if let Some(channel) = pdm_state.channels.get(&channel_id) {
                channel.status == ChannelStatus::Off
            } else {
                return Err(StatusCode::NOT_FOUND);
            }
        },
        crate::models::ChannelAction::SetCurrentLimit(_limit) => {
            // TODO: Implement current limit setting
            return Ok(Json(json!({
                "success": false,
                "message": "Current limit setting not yet implemented"
            })));
        }
    };
    
    // Send command to hardware
    match state.hardware_manager.control_channel(channel_id, enable).await {
        Ok(()) => {
            // Update state
            let mut pdm_state = state.pdm_state.write().await;
            if let Some(channel) = pdm_state.channels.get_mut(&channel_id) {
                channel.status = if enable { ChannelStatus::On } else { ChannelStatus::Off };
                channel.last_update = chrono::Utc::now();
            }
            
            Ok(Json(json!({
                "success": true,
                "channel": channel_id,
                "status": if enable { "ON" } else { "OFF" },
                "message": format!("Channel {} {}", channel_id, if enable { "enabled" } else { "disabled" })
            })))
        },
        Err(e) => {
            error!("Failed to control channel {}: {}", channel_id, e);
            Ok(Json(json!({
                "success": false,
                "message": format!("Hardware error: {}", e)
            })))
        }
    }
}

/// Toggle a channel on/off
async fn toggle_channel(
    Path(channel_id): Path<u8>,
    State(state): State<AppState>,
) -> Result<Json<Value>, StatusCode> {
    let request = ChannelControlRequest {
        channel: channel_id,
        action: crate::models::ChannelAction::Toggle,
    };
    
    control_channel(Path(channel_id), State(state), Json(request)).await
}

/// Emergency shutdown all channels
async fn emergency_shutdown(
    State(state): State<AppState>,
    Json(_request): Json<EmergencyShutdownRequest>,
) -> Result<Json<Value>, StatusCode> {
    info!("🚨 EMERGENCY SHUTDOWN requested");
    
    match state.hardware_manager.emergency_shutdown().await {
        Ok(()) => {
            // Update state
            let mut pdm_state = state.pdm_state.write().await;
            pdm_state.emergency_shutdown();
            
            Ok(Json(json!({
                "success": true,
                "message": "Emergency shutdown completed - all channels OFF",
                "timestamp": chrono::Utc::now()
            })))
        },
        Err(e) => {
            error!("Emergency shutdown failed: {}", e);
            Ok(Json(json!({
                "success": false,
                "message": format!("Emergency shutdown failed: {}", e)
            })))
        }
    }
}

/// Reset all channels to OFF state
async fn reset_all_channels(State(state): State<AppState>) -> Result<Json<Value>, StatusCode> {
    info!("Reset all channels requested");
    
    let mut success_count = 0;
    let mut errors = Vec::new();
    
    // Turn off all channels individually
    for channel_id in 1..=8 {
        match state.hardware_manager.control_channel(channel_id, false).await {
            Ok(()) => success_count += 1,
            Err(e) => errors.push(format!("Channel {}: {}", channel_id, e)),
        }
    }
    
    // Update state
    {
        let mut pdm_state = state.pdm_state.write().await;
        for channel in pdm_state.channels.values_mut() {
            channel.status = ChannelStatus::Off;
            channel.voltage = 0.0;
            channel.current = 0.0;
            channel.last_update = chrono::Utc::now();
        }
        pdm_state.total_current = 0.0;
        pdm_state.last_update = chrono::Utc::now();
    }
    
    Ok(Json(json!({
        "success": errors.is_empty(),
        "channels_reset": success_count,
        "errors": errors,
        "message": if errors.is_empty() {
            "All channels reset successfully"
        } else {
            "Some channels failed to reset"
        }
    })))
}

/// Get current configuration
async fn get_config(_state: State<AppState>) -> Result<Json<Value>, StatusCode> {
    // TODO: Return sanitized configuration (no sensitive data)
    Ok(Json(json!({
        "api_version": "1.0.0",
        "max_channels": 8,
        "features": ["channel_control", "emergency_shutdown", "real_time_monitoring"],
        "hardware_mode": "simulation" // TODO: Read from actual config
    })))
}
