/**
 * Configuration Management for PDM Backend
 * 
 * This module handles loading and managing configuration settings:
 * - Server settings (port, address)
 * - Hardware communication settings
 * - Safety limits and thresholds
 * - Logging configuration
 */

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::fs;

/// Main configuration structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Server configuration
    pub server_address: String,
    pub api_version: String,
    
    /// Hardware configuration
    pub hardware: HardwareConfig,
    
    /// Safety configuration
    pub safety: SafetyConfig,
    
    /// Logging configuration
    pub logging: LoggingConfig,
}

/// Hardware communication settings
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareConfig {
    /// USB/Serial port for PDM communication
    pub serial_port: Option<String>,
    pub serial_baud_rate: u32,
    
    /// CAN bus settings
    pub can_interface: Option<String>,
    pub can_bitrate: u32,
    
    /// Update intervals
    pub status_update_interval_ms: u64,
    pub monitoring_interval_ms: u64,
    
    /// Hardware simulation mode (for development)
    pub simulation_mode: bool,
}

/// Safety limits and thresholds
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SafetyConfig {
    /// Maximum input voltage before fault (V)
    pub max_input_voltage: f32,
    /// Minimum input voltage before fault (V)
    pub min_input_voltage: f32,
    
    /// Maximum total current before emergency shutdown (A)
    pub max_total_current: f32,
    
    /// Maximum PDM temperature before fault (°C)
    pub max_temperature: f32,
    
    /// Default current limit per channel (A)
    pub default_channel_current_limit: f32,
    
    /// Emergency shutdown timeout (seconds)
    pub emergency_shutdown_timeout: u64,
}

/// Logging configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoggingConfig {
    /// Log level (trace, debug, info, warn, error)
    pub level: String,
    /// Log to file
    pub log_to_file: bool,
    /// Log file path
    pub log_file_path: Option<String>,
}

impl Config {
    /// Load configuration from file or create default
    pub fn load() -> Result<Self> {
        const CONFIG_FILE: &str = "pdm_config.toml";
        
        if std::path::Path::new(CONFIG_FILE).exists() {
            // Load from file
            let config_str = fs::read_to_string(CONFIG_FILE)?;
            let config: Config = toml::from_str(&config_str)?;
            Ok(config)
        } else {
            // Create default configuration
            let config = Self::default();
            config.save()?;
            Ok(config)
        }
    }
    
    /// Save configuration to file
    pub fn save(&self) -> Result<()> {
        const CONFIG_FILE: &str = "pdm_config.toml";
        let config_str = toml::to_string_pretty(self)?;
        fs::write(CONFIG_FILE, config_str)?;
        Ok(())
    }
}

impl Default for Config {
    fn default() -> Self {
        Self {
            server_address: "127.0.0.1:3030".to_string(),
            api_version: "1.0.0".to_string(),
            
            hardware: HardwareConfig {
                serial_port: None, // Auto-detect
                serial_baud_rate: 115200,
                can_interface: Some("can0".to_string()),
                can_bitrate: 500000, // 500kbps
                status_update_interval_ms: 100, // 10Hz
                monitoring_interval_ms: 50,     // 20Hz
                simulation_mode: true, // Start in simulation mode
            },
            
            safety: SafetyConfig {
                max_input_voltage: 16.0,
                min_input_voltage: 10.0,
                max_total_current: 100.0,
                max_temperature: 85.0,
                default_channel_current_limit: 15.0,
                emergency_shutdown_timeout: 5,
            },
            
            logging: LoggingConfig {
                level: "info".to_string(),
                log_to_file: true,
                log_file_path: Some("pdm_backend.log".to_string()),
            },
        }
    }
}

// Add toml dependency to Cargo.toml
use toml;
