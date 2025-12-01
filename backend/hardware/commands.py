from hardware.protobuf import AvailableChannels, ProtoBuff
from .usb_devices import USBDevices

class Commands:
    @staticmethod 
    def command_add_channel(device: str) -> None:
        usb_device = USBDevices(9600)
        usb_device.connection(device)
        usb_device.send_msg(ProtoBuff.new_channel())
        usb_device.close_connection()
    @staticmethod 
    def command_set_channel(device: str, channel_number: int, status: bool) -> None:
        usb_device = USBDevices(9600)
        usb_device.connection(device)
        usb_device.send_msg(ProtoBuff.set_channel(AvailableChannels(channel_number), status))
        usb_device.close_connection()
    @staticmethod
    def command_get_param(device: str, channel_number: int) -> None:
        usb_device = USBDevices(9600)
        usb_device.connection(device)
        usb_device.send_msg(ProtoBuff.get_params(AvailableChannels(channel_number)))
        usb_device.recv_msg()
        usb_device.close_connection()
    @staticmethod
    def command_set_current(device: str, channel_number: int, current_limit: float) -> None:
        usb_device = USBDevices(9600)
        usb_device.connection(device)
        
        usb_device.send_msg(ProtoBuff.set_current_lmit(AvailableChannels(channel_number), current_limit))
        usb_device.close_connection()

