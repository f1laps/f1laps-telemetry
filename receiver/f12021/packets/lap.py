import ctypes

from lib.logger import log
from .base import PacketBase, PacketHeader

MAX_DISTANCE_COUNT_AS_NEW_LAP = 200


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
    ]

    def process(self, session):
        # Get lap number and distance
        lap_number = self.get_lap_number()
        if not lap_number:
            # If we can't retrieve lap number, we can't do anything here
            log.debug("Can't retrieve lap number from lap packet - not processing")
            return session
        lap_distance = self.get_lap_distance()
        # session.lap_distance = lap_distance # Enable this for motion packet / minimap

        # Handle in- and outlaps - essentially ignore everything, just update lap before outlap
        # Race sessions have 1 outlap at the end
        if session.is_race() or session.is_qualifying_one_shot():
            is_out_or_inlap = self.is_race_inlap(session, lap_number)
        # Quali sessions have inlaps and outlaps
        elif session.is_qualifying_non_one_shot():
            is_out_or_inlap = self.is_quali_out_or_inlap(session, lap_number)
        else: # time trial, practive
            is_out_or_inlap = False
        
        if is_out_or_inlap:
            if not session.current_lap_in_outlap_logging_status:
                log.info("Skipping lap #%s because it's an in-/outlap" % lap_number)
                # In normal quali, the inlap is #n+1; In race it's #n
                last_valid_lap_number = lap_number if not session.is_qualifying_non_one_shot() else lap_number - 1
                self.update_previous_lap(session, last_valid_lap_number+1) # +1 because we're updating the previous lap
                session.complete_lap_v2(last_valid_lap_number)
            # Make sure to not log for this lap anymore
            session.current_lap_in_outlap_logging_status = True
            return session
        else:
            # Perform clean-up of previous in-/outlap data 
            if session.current_lap_in_outlap_logging_status:
                # Drop all data of this lap, so that telemetry gets reset
                lap_number_to_drop = lap_number + 1 if not session.is_qualifying_non_one_shot() else lap_number
                session.drop_lap_data(lap_number_to_drop)
                # Reset outlap logger
                session.current_lap_in_outlap_logging_status = False

        # Handle new laps
        if self.is_new_lap(session, lap_number):
            # Update previous lap with sector 3 time
            self.update_previous_lap(session, lap_number)
            # Start new lap, which in turn starts telemetry
            session.start_new_lap(lap_number)
            # Push lap-1 to F1Laps
            session.complete_lap_v2(lap_number-1)

        # Update current lap and telemetry
        session = self.update_current_lap(session)
        session = self.update_telemetry(session)
        return session

    def update_current_lap(self, session):
        lap_data = self.lapData[self.header.playerCarIndex]
        lap_number = self.get_lap_number()
        # Update lap list data
        if not self.packet_should_update_lap(session, lap_number):
            log.info("Not updating lap #%s with 0 value because it's already set" % lap_number)
            return session
        session.lap_list[lap_number]["lap_number"]        = lap_data.currentLapNum
        session.lap_list[lap_number]["car_race_position"] = lap_data.carPosition
        session.lap_list[lap_number]["pit_status"]        = self.get_pit_value(session, lap_data, lap_number)
        session.lap_list[lap_number]["is_valid"]          = False if lap_data.currentLapInvalid == 1 else True
        session.lap_list[lap_number]["sector_1_ms"]       = lap_data.sector1TimeInMS
        session.lap_list[lap_number]["sector_2_ms"]       = lap_data.sector2TimeInMS
        session.lap_list[lap_number]["sector_3_ms"]       = self.get_sector_3_ms(lap_data)
        return session

    def packet_should_update_lap(self, session, lap_number):
        """ 
        Check if the new data is allowed to overwrite existing data
        Only allow packets to write data if we don't already have all 3 sectors 
        """
        # For time trial, we should always overwrite
        if session.is_time_trial():
            return True
        null_values = ["0", 0, None, ""]
        lap_data = self.lapData[self.header.playerCarIndex]
        lap_list = session.lap_list[lap_number]
        all_sectors_set = lap_list.get("sector_1_ms") and lap_list.get("sector_2_ms") and lap_list.get("sector_3_ms")
        if all_sectors_set and lap_data.sector1TimeInMS in null_values:
            return False
        return True

    def update_previous_lap(self, session, lap_number):
        lap_data = self.lapData[self.header.playerCarIndex]
        prev_lap_num = lap_number - 1
        if not session.lap_list.get(prev_lap_num) or \
           not (session.lap_list[prev_lap_num]["sector_1_ms"] and session.lap_list[prev_lap_num]["sector_2_ms"]):
            log.info("Lap packet: not updating previous lap %s because it doesn't exist" % prev_lap_num)
            return
        # Calculate sector 3 time (so that it adds up to actual last lap time)
        sector_3_ms = lap_data.lastLapTimeInMS - session.lap_list[prev_lap_num]["sector_1_ms"] - session.lap_list[prev_lap_num]["sector_2_ms"]
        session.lap_list[prev_lap_num]["sector_3_ms"] = sector_3_ms

    def get_lap_number(self):
        try:
            lap_data = self.lapData[self.header.playerCarIndex]
        except:
            return None
        return lap_data.currentLapNum

    def get_sector_3_ms(self, lap_data):
        sector_3_ms = lap_data.currentLapTimeInMS - lap_data.sector1TimeInMS - lap_data.sector2TimeInMS
        return round(sector_3_ms) if sector_3_ms else None 

    def is_new_lap(self, session, lap_number):
        """ Empty dict {} should not count as new lap, so test for None only """
        return session.lap_list.get(lap_number) is None

    def is_race_inlap(self, session, lap_number):
        # For race or OSQ inlaps (lap after last lap), the lap number doesn't increment
        # We use the following test to ignore the inlap
        lap_list = session.lap_list.get(lap_number)
        current_distance = self.get_lap_distance()
        # If we're in the first x meters of a lap and also have all sector data -- it's an inlap
        if (current_distance and current_distance < MAX_DISTANCE_COUNT_AS_NEW_LAP) and \
           (lap_list and lap_list.get("sector_1_ms") and lap_list.get("sector_2_ms") and lap_list.get("sector_3_ms")):
            log.info("Skipping lap #%s because it's an inlap" % lap_number)
            return True
        return False

    def is_quali_out_or_inlap(self, session, lap_number):
        # For qualifying sessions (non-OSQ), the inlap and outlaps need to be ignored
        # We check this based on pit status -- if no pits on entire lap, it's a real lap
        lap_data = self.lapData[self.header.playerCarIndex]
        return lap_data.pitStatus != 0

    def get_lap_distance(self):
        lap_data = self.lapData[self.header.playerCarIndex]
        return lap_data.lapDistance

    def update_telemetry(self, session):
        lap_data = self.lapData[self.header.playerCarIndex]
        frame = self.header.frameIdentifier
        session.telemetry.set(frame, lap_time     = lap_data.currentLapTimeInMS,
                                     lap_distance = lap_data.lapDistance)
        return session

    def get_pit_value(self, session, lap_data, lap_number):
        # pit status changes over the course of a lap
        # we want to keep the highest number of 
        # 0 = no pit; 1 = pit entry/exit; 2 = pitting
        # so that we store the "slowest" pit value
        if session.lap_list.get(lap_number) and session.lap_list[lap_number].get("pit_status"):
            return max(session.lap_list[lap_number]["pit_status"], lap_data.pitStatus)
        else:
            return lap_data.pitStatus

