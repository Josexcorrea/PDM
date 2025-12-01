from enum import Enum 

class Commands(Enum):
    NEW_CHANNEL=0x00 
    SET_CHANNEL=0x01
    GET_PARAMS=0x02
    SET_CURRENT=0x03


class Status(Enum):
    ON=0x1
    OFF=0x0

class AvailableChannels(Enum):
    CHANNEL_ONE=0x01 
    CHANNEL_TWO=0x02
    CHANNEL_THREE=0x03

class ProtoBuff:
    @staticmethod
    def new_channel() -> bytearray: 
        return bytearray([Commands.NEW_CHANNEL.value])
    @staticmethod
    def set_channel(channel: AvailableChannels, status: bool) -> bytearray: 
        return bytearray([Commands.SET_CHANNEL.value, channel.value, Status.ON.value if status else Status.OFF.value])
    @staticmethod 
    def get_params(channel: AvailableChannels) -> bytearray:
        return bytearray([Commands.GET_PARAMS.value, channel.value])
    @staticmethod 
    def set_current_lmit(channel: AvailableChannels, value: float) -> bytearray:
        val = int(value * 255)
        print(val, value)
        return bytearray([Commands.SET_CURRENT.value, channel.value, int(value * 255)])
