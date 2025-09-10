/**
 * Data Models for PDM Backend
 * 
 * This module defines all the data structures used throughout the backend:
 * - Channel states and configurations
 * - System status and metrics
 * - API request/response types
 * - Hardware communication protocols
 */

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use std::collections::HashMap;

/// Represents the status of a single PDM channel
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Channel {
    /// Channel number (1-8)
    pub ch: u8,
    /// Human-readable channel name
    pub name: String,
    /// Current voltage reading (V)
    pub voltage: f32,
    /// Current amperage reading (A)
    pub current: f32,
    /// Channel status (ON/OFF)
    pub status: ChannelStatus,
    /// Maximum current limit for this channel (A)
    pub current_limit: f32,
    /// Fault status
    pub fault: Option<ChannelFault>,
    /// Last update timestamp
    pub last_update: DateTime<Utc>,
}

/// Channel status enumeration
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ChannelStatus {
    #[serde(rename = "ON")]
    On,
    #[serde(rename = "OFF")]
    Off,
    #[serde(rename = "FAULT")]
    Fault,
}

/// Channel fault types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ChannelFault {
    Overcurrent,
    Overvoltage,
    Undervoltage,
    ShortCircuit,
    OpenLoad,
    Overtemperature,
}

/// Overall PDM system state
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PdmState {
    /// All 8 channels
    pub channels: HashMap<u8, Channel>,
    /// Input voltage from main power supply
    pub input_voltage: f32,
    /// Total current consumption across all channels
    pub total_current: f32,
    /// PDM internal temperature (°C)
    pub temperature: f32,
    /// System status
    pub system_status: SystemStatus,
    /// Last system update timestamp
    pub last_update: DateTime<Utc>,
}

/// System-wide status
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SystemStatus {
    Normal,
    Warning,
    Fault,
    Emergency,
}

/// API request to control a channel
#[derive(Debug, Deserialize)]
pub struct ChannelControlRequest {
    pub channel: u8,
    pub action: ChannelAction,
}

/// Channel control actions
#[derive(Debug, Deserialize)]
pub enum ChannelAction {
    TurnOn,
    TurnOff,
    Toggle,
    SetCurrentLimit(f32),
}

/// API request for emergency shutdown
#[derive(Debug, Deserialize)]
pub struct EmergencyShutdownRequest {
    pub reason: String,
}

/// API response for system status
#[derive(Debug, Serialize)]
pub struct SystemStatusResponse {
    pub pdm_state: PdmState,
    pub uptime_seconds: u64,
    pub api_version: String,
}

/// Hardware communication message
#[derive(Debug)]
pub enum HardwareMessage {
    ChannelControl {
        channel: u8,
        enable: bool,
    },
    SetCurrentLimit {
        channel: u8,
        limit_amps: f32,
    },
    EmergencyShutdown,
    RequestStatus,
}

/// Hardware response message
#[derive(Debug)]
pub enum HardwareResponse {
    ChannelStatus {
        channel: u8,
        voltage: f32,
        current: f32,
        status: ChannelStatus,
        fault: Option<ChannelFault>,
    },
    SystemStatus {
        input_voltage: f32,
        temperature: f32,
        total_current: f32,
    },
    CommandAck {
        success: bool,
        message: String,
    },
}

impl PdmState {
    /// Create a new PDM state with default values
    pub fn new() -> Self {
        let mut channels = HashMap::new();
        
        // Initialize all 8 channels with default values
        let channel_names = [
            "FUEL PUMP", "IGNITION", "COOLING FAN", "HEADLIGHTS",
            "ECU MAIN", "SPARE 1", "SPARE 2", "SPARE 3"
        ];
        
        for i in 1..=8 {
            channels.insert(i, Channel {
                ch: i,
                name: channel_names[(i - 1) as usize].to_string(),
                voltage: 0.0,
                current: 0.0,
                status: ChannelStatus::Off,
                current_limit: 15.0, // Default 15A limit
                fault: None,
                last_update: Utc::now(),
            });
        }
        
        Self {
            channels,
            input_voltage: 12.0,
            total_current: 0.0,
            temperature: 25.0,
            system_status: SystemStatus::Normal,
            last_update: Utc::now(),
        }
    }
    
    /// Update a channel's status
    pub fn update_channel(&mut self, channel: u8, voltage: f32, current: f32, status: ChannelStatus) {
        if let Some(ch) = self.channels.get_mut(&channel) {
            ch.voltage = voltage;
            ch.current = current;
            ch.status = status;
            ch.last_update = Utc::now();
        }
        self.last_update = Utc::now();
    }
    
    /// Emergency shutdown all channels
    pub fn emergency_shutdown(&mut self) {
        for channel in self.channels.values_mut() {
            channel.status = ChannelStatus::Off;
            channel.voltage = 0.0;
            channel.current = 0.0;
            channel.last_update = Utc::now();
        }
        self.total_current = 0.0;
        self.last_update = Utc::now();
    }
    
    /// Calculate total power consumption
    pub fn total_power(&self) -> f32 {
        self.input_voltage * self.total_current
    }
}
