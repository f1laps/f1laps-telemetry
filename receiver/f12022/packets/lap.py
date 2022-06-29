import ctypes

import logging
log = logging.getLogger(__name__)

from .base import PacketBase, PacketHeader


class LapData(PacketBase):

    _fields_ = [
        ("lastLapTimeInMS", ctypes.c_uint32),
        ("currentLapTimeInMS", ctypes.c_uint32),
        ("sector1TimeInMS", ctypes.c_uint16), 
        ("sector2TimeInMS", ctypes.c_uint16),
        ("lapDistance", ctypes.c_float),
        ("totalDistance", ctypes.c_float),
        ("safetyCarDelta", ctypes.c_float),
        ("carPosition", ctypes.c_uint8),
        ("currentLapNum", ctypes.c_uint8),
        ("pitStatus", ctypes.c_uint8), # 0 = none, 1 = pitting, 2 = in pit area
        ("numPitStops", ctypes.c_uint8), # Number of pit stops taken in this race
        ("sector", ctypes.c_uint8), # 0 = sector1, 1 = sector2, 2 = sector3
        ("currentLapInvalid", ctypes.c_uint8), # Current lap invalid - 0 = valid, 1 = invalid
        ("penalties", ctypes.c_uint8),
        ("warnings", ctypes.c_uint8),
        ("numUnservedDriveThroughPens", ctypes.c_uint8),
        ("numUnservedStopGoPens", ctypes.c_uint8),
        ("gridPosition", ctypes.c_uint8),
        ("driverStatus", ctypes.c_uint8), # Status of driver - 0 = in garage, 1 = flying lap
                                          # 2 = in lap, 3 = out lap, 4 = on track
        ("resultStatus", ctypes.c_uint8), # Result status - 0 = invalid, 1 = inactive, 2 = active
                                          # 3 = finished, 4 = didnotfinish, 5 = disqualified
                                          # 6 = not classified, 7 = retired
        ("pitLaneTimerActive", ctypes.c_uint8),
        ("pitLaneTimeInLaneInMS", ctypes.c_uint16),
        ("pitStopTimerInMS", ctypes.c_uint16),
        ("pitStopShouldServePen", ctypes.c_uint8),
    ]


class PacketLapData(PacketBase):
    """
    The lap data packet gives details of all the cars in the session.
    Frequency: Rate as specified in menus
    Size: 904 bytes
    Version: 1
    """

    _fields_ = [
        ("header", PacketHeader),  # Header
        ("lapData", LapData * 22),  # Lap data for all cars on track
        ("timeTrialPBCarIdx", ctypes.c_uint8), # Index of Personal Best car in time trial (255 if invalid)
        ("timeTrialRivalCarIdx", ctypes.c_uint8), # Index of Rival car in time trial (255 if invalid)
    ]

    def serialize(self):
        try:
            lap_data = self.lapData[self.header.playerCarIndex]
        except:
            return None
        return {
            "packet_type": "lap",
            "lap_number": lap_data.currentLapNum,
            "car_race_position": lap_data.carPosition,
            "pit_status": lap_data.pitStatus,
            "is_valid": bool(lap_data.currentLapInvalid != 1),
            "current_laptime_ms": lap_data.currentLapTimeInMS,
            "last_laptime_ms": lap_data.lastLapTimeInMS,
            "sector_1_ms": lap_data.sector1TimeInMS,
            "sector_2_ms": lap_data.sector2TimeInMS,
            "sector_3_ms": self.get_sector_3_ms(lap_data),
            "lap_distance": lap_data.lapDistance,
            "frame_identifier": self.header.frameIdentifier
        }
    
    def get_sector_3_ms(self, lap_data):
        if not (lap_data.sector1TimeInMS and lap_data.sector2TimeInMS):
            return None
        sector_3_time = lap_data.currentLapTimeInMS - lap_data.sector1TimeInMS - lap_data.sector2TimeInMS
        return round(sector_3_time) if sector_3_time else None
