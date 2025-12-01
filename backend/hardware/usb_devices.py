import platform
import os
import serial
from enum import Enum 

class OperatingSystems(Enum):
    LINUX="linux"
    MACOS="macos"
    WIN="windows"

class USBDevices:
    def __init__(self, baudrate: int) -> None:
        self.operating_system: str = platform.system().lower() 
        self.device_list: list[str] = self.find_devices() 
        self.baudrate: int = baudrate 
        self.device: serial.Serial
    def connection(self, device: str) -> None: 
        print(device)
        self.device = serial.Serial(f"/dev/{device}", 115200, timeout=120)
    def close_connection(self) -> None:
        self.device.close()
    def send_msg(self, byte_stream: bytearray) -> None: 
        print(bytes(byte_stream))
        self.device.write(bytes(byte_stream))
    def recv_msg(self) -> None:
        response = self.device.readline()
        print(f"Received: {response.strip()}")
        return
    def find_devices(self) -> list[str]: 
        if self.operating_system == OperatingSystems.LINUX.value:
            devices = os.listdir("/dev")
            filtered_devices = list(filter(lambda x: x.find("tty") != -1, devices))
            return filtered_devices
        elif self.operating_system == OperatingSystems.MACOS.value:
            return []
        elif self.operating_system == OperatingSystems.WIN.value:
            return []
        return []

