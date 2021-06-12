import ctypes

from .base import PacketBase, PacketHeader


class LapHistoryData(PacketBase):
    _fields_ = [
        ("lapTimeInMS", ctypes.c_uint16),
        ("sector1TimeInMS", ctypes.c_uint16),
        ("sector2TimeInMS", ctypes.c_uint16),
        ("sector3TimeInMS", ctypes.c_uint16),
    ]


class TyreStintsHistoryData(PacketBase):
    _fields_ = [
        ("endLap", ctypes.c_uint8),
        ("tyreActualCompound", ctypes.c_uint8), # Actual tyres used by this driver
        ("tyreVisualCompound", ctypes.c_uint8), # Visual tyres used by this driver
    ]


class PacketSessionHistoryData(PacketBase):
    """
    This packet contains lap times and tyre usage for the session. 
    This packet works slightly differently to other packets. 
    To reduce CPU and bandwidth, each packet relates to a specific vehicle and is sent every 1/20 s, 
    and the vehicle being sent is cycled through. 
    Therefore in a 20 car race you should receive an update for each vehicle at least once per second.
 
    Frequency: 20 per second but cycling through cars
    Size: 1055 bytes
    Version: 1
    """
    _fields_ = [
        ("header", PacketHeader),  # Header
        ("carIdx", ctypes.c_uint8),  # Index of the car this lap data relates to
        ("numLaps", ctypes.c_uint8),  # Num laps in the data (including current partial lap)
        ("numTyreStints", ctypes.c_uint8),  # Number of tyre stints in the data
        ("bestLapTimeLapNum", ctypes.c_uint8),  # Lap the best lap time was achieved on
        ("bestSector1LapNum", ctypes.c_uint8),  # Lap the best Sector 1 time was achieved on
        ("bestSector2LapNum", ctypes.c_uint8),  # Lap the best Sector 2 time was achieved on
        ("bestSector3LapNum", ctypes.c_uint8),  # Lap the best Sector 3 time was achieved on
        ("lapHistoryData", LapHistoryData * 22),
        ("tyreStintsHistoryData", TyreStintsHistoryData * 22),
    ]
