import ctypes

from .base import PacketBase, PacketHeader


class LapData(PacketBase):

    _fields_ = [
        ("lastLapTime", ctypes.c_float), # in sec
        ("currentLapTime", ctypes.c_float), # in sec 
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
    ]

    def process(self, session):
        self.update_current_lap(session)
        return session

    def update_current_lap(self, session):
        lap_data = self.lapData[self.header.playerCarIndex]
        lap_number = lap_data.currentLapNum
        if not session.lap_list.get(lap_number):
            session.lap_list[lap_number] = {}
            session.new_lap_started(lap_number)
        session.lap_list[lap_number]["car_race_position"] = lap_data.carPosition
        session.lap_list[lap_number]["pit_status"]        = self.get_pit_value(session, lap_data, lap_number)
        session.lap_list[lap_number]["is_valid"]          = False if lap_data.currentLapInvalid == 1 else True
        return session

    def update_telemetry(self, session):
        lap_data = self.lapData[self.header.playerCarIndex]
        frame = self.header.frameIdentifier
        total_lap_time = lap_data.currentLapTime * 1000 # current lap time is in secs not ms
        session.telemetry.set(frame, lap_time     = total_lap_time,
                                     lap_distance = lap_data.lapDistance)
        return session

    def get_pit_value(self, session, lap_data, lap_number):
        # pit status changes over the course of a lap
        # we want to keep the highest number of 
        # 0 = no pit; 1 = pit entry/exit; 2 = pitting
        # so that we store the "slowest" pit value
        if session.lap_list[lap_number].get("pit_status"):
            return max(session.lap_list[lap_number]["pit_status"], lap_data.pitStatus)
        else:
            return lap_data.pitStatus

