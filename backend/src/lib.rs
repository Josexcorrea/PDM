/**
 * Backend Tests
 * 
 * Basic tests to verify the PDM backend functionality
 */

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::{PdmState, ChannelStatus};
    use crate::config::Config;
    
    #[test]
    fn test_pdm_state_creation() {
        let state = PdmState::new();
        
        // Should have 8 channels
        assert_eq!(state.channels.len(), 8);
        
        // All channels should start OFF
        for channel in state.channels.values() {
            assert_eq!(channel.status, ChannelStatus::Off);
            assert_eq!(channel.voltage, 0.0);
            assert_eq!(channel.current, 0.0);
        }
        
        // System should start normal
        assert!(matches!(state.system_status, crate::models::SystemStatus::Normal));
    }
    
    #[test]
    fn test_channel_update() {
        let mut state = PdmState::new();
        
        // Update channel 1
        state.update_channel(1, 13.2, 4.5, ChannelStatus::On);
        
        let channel = state.channels.get(&1).unwrap();
        assert_eq!(channel.voltage, 13.2);
        assert_eq!(channel.current, 4.5);
        assert_eq!(channel.status, ChannelStatus::On);
    }
    
    #[test]
    fn test_emergency_shutdown() {
        let mut state = PdmState::new();
        
        // Turn on some channels first
        state.update_channel(1, 13.2, 4.5, ChannelStatus::On);
        state.update_channel(2, 13.1, 2.1, ChannelStatus::On);
        
        // Emergency shutdown
        state.emergency_shutdown();
        
        // All channels should be OFF
        for channel in state.channels.values() {
            assert_eq!(channel.status, ChannelStatus::Off);
            assert_eq!(channel.voltage, 0.0);
            assert_eq!(channel.current, 0.0);
        }
        
        assert_eq!(state.total_current, 0.0);
    }
    
    #[test]
    fn test_total_power_calculation() {
        let mut state = PdmState::new();
        state.input_voltage = 13.8;
        state.total_current = 10.0;
        
        let power = state.total_power();
        assert_eq!(power, 138.0); // 13.8V * 10.0A = 138W
    }
    
    #[test]
    fn test_config_default() {
        let config = Config::default();
        
        assert_eq!(config.server_address, "127.0.0.1:3030");
        assert_eq!(config.api_version, "1.0.0");
        assert!(config.hardware.simulation_mode);
        assert_eq!(config.safety.max_total_current, 100.0);
    }
    
    #[tokio::test]
    async fn test_hardware_manager_creation() {
        let config = Config::default();
        let hardware_manager = crate::hardware::HardwareManager::new(config);
        
        assert!(hardware_manager.is_ok());
    }
}
