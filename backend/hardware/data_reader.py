"""
Data Reader Module for PDM USB Communication

This module handles continuous reading and parsing of data from the USB device.
It updates the global pdm_data store with real-time values.
"""

import threading
import time
from datetime import datetime
from typing import Dict, Any
from hardware.usb_devices import USBDevices
from hardware.protobuf import AvailableChannels, ProtoBuff


class DataReader:
    """Background thread that continuously reads data from USB device"""
    
    def __init__(self, device: str, baudrate: int = 9600):
        self.device = device
        self.baudrate = baudrate
        self.running = False
        self.thread = None
        self.usb_device = None
        
    def start(self, pdm_data: Dict[str, Any], data_lock: threading.Lock):
        """Start the background data reading thread"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(
            target=self._read_loop,
            args=(pdm_data, data_lock),
            daemon=True
        )
        self.thread.start()
        
    def stop(self):
        """Stop the background data reading thread"""
        self.running = False
        if self.usb_device:
            try:
                self.usb_device.close_connection()
            except:
                pass
        if self.thread:
            self.thread.join(timeout=2)
            
    def _read_loop(self, pdm_data: Dict[str, Any], data_lock: threading.Lock):
        """Main loop that reads data from USB and updates pdm_data"""
        try:
            self.usb_device = USBDevices(self.baudrate)
            self.usb_device.connection(self.device)
        except Exception as e:
            print(f"Failed to connect to USB device {self.device}: {e}")
            self.running = False
            return
            
        while self.running:
            try:
                # Request channel parameters for each channel
                # This is a simplified approach - you may need to adjust based on your protocol
                for channel_idx in range(8):
                    if not self.running:
                        break
                        
                    try:
                        # Request parameters for this channel
                        self.usb_device.send_msg(
                            ProtoBuff.get_params(AvailableChannels(channel_idx + 1))
                        )
                        
                        # Read response
                        response = self.usb_device.recv_msg()
                        
                        # Parse response and update data
                        # NOTE: You'll need to adjust this based on your actual protocol
                        # This is a placeholder that assumes response is a string
                        if response:
                            with data_lock:
                                # Update timestamp
                                pdm_data["timestamp"] = datetime.now().isoformat()
                                
                                # Update channel data (placeholder - adjust to your protocol)
                                # For now, we'll keep the mock data but you can parse 'response' here
                                pass
                                
                    except Exception as e:
                        print(f"Error reading channel {channel_idx}: {e}")
                
                # Small delay between polling cycles
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in read loop: {e}")
                time.sleep(1)  # Wait before retrying
                
        # Cleanup
        try:
            self.usb_device.close_connection()
        except:
            pass


# Global data reader instance (optional - can be initialized in route.py)
_data_reader = None


def start_data_reader(device: str, pdm_data: Dict[str, Any], data_lock: threading.Lock):
    """Initialize and start the global data reader"""
    global _data_reader
    if _data_reader is None:
        _data_reader = DataReader(device)
    _data_reader.start(pdm_data, data_lock)
    

def stop_data_reader():
    """Stop the global data reader"""
    global _data_reader
    if _data_reader:
        _data_reader.stop()
