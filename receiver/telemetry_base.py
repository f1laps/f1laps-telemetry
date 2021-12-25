from lib.logger import log
from lib.file_handler import get_path_executable_parent
import json

KEY_INDEX_MAP = {
    "lap_distance": 0,
    "lap_time"    : 1,
    "speed"       : 2,
    "brake"       : 3,
    "throttle"    : 4,
    "gear"        : 5,
    "steer"       : 6,
    "drs"         : 7,
}

KEY_ROUND_MAP = {
    "lap_distance": 2,
    "lap_time"    : 0,
    "speed"       : 0,
    "brake"       : 3,
    "throttle"    : 3,
    "gear"        : 0,
    "steer"       : 3,
    "drs"         : 0,
}


class TelemetryLapBase:
    """
    Stores current lap telemetry data in memory
    """

    # Time trial lets you restart a lap
    # Other game modes have outlaps (TT doesnt)
    # This distinction is important because for outlaps, we dont want the outlap frames
    # But for restart, we want the new lap frames
    SESSION_TYPES_WITHOUT_OUTLAP = [1, 2, 3, 4, 13]

    def __init__(self, number, session_type=None):
        # Current lap number
        self.number = number

        self.session_type = session_type

        # Each frame is a key in this dict
        # Each holds a list of the telemetry values
        self.frame_dict = {}

        # Store which frames got popped 
        self.frames_popped_list = []

        # Ensure we're incrementing lap distance
        # If we don't, we need to remove the dict
        self.last_lap_distance = None

        self.MAX_FLASHBACK_DISTANCE_METERS = 1500
        self.MAX_DISTANCE_COUNT_AS_NEW_LAP = 200

    def clean_frame(self, frame_number):
        frame = self.frame_dict.get(frame_number)
        current_distance = None
        if not frame:
            return

        # Check if we popped this frame before - if so, don't populate it again
        if frame_number in self.frames_popped_list:
            self.frame_dict.pop(frame_number)
            return 

        # Get lap distance of current frame
        current_distance = frame[KEY_INDEX_MAP["lap_distance"]]

        # The telemetry packet doesn't set lap distance, so we may not have distance yet - return if so
        if not current_distance:
            return

        # This should never happen, but let's make sure that distance is a number
        if not isinstance(current_distance, float) and not isinstance(current_distance, int):
            return

        # Reset telemetry when we are pre session FIRST LINE CROSS start
        if current_distance < 0:
            self.frame_dict = {}
            # In F1 2021, in an outlap in TT, the first frame sends a positive value (e.g. distance of 126)
            # Then switches to negative values as expected in an outlap
            # So we need to manually reset the last lap distance to None here
            self.last_lap_distance = None
            return

        # If we have current and last lap distance, check that we're incrementing the distance
        if self.last_lap_distance:    

            # Check if last distance was higher - this means something UNEXPECTED happened
            if self.last_lap_distance > current_distance:
                # We came out of the garage, which doesnt increment the lap counter (weird!)
                # And lap distance pre line cross is NOT negative (also weird!)
                # So if we drop the current distance down to a super small number, we assume a NEW LAP was started
                if current_distance < self.MAX_DISTANCE_COUNT_AS_NEW_LAP:
                    # New in F1 2021:
                    # Sometimes, the Lap Package gets sent after finish line cross (inlap) without incrementing the lapnumber
                    # In that case, the following code would remove the entire last lap. We dont want that. 
                    # So we add the condition that we only clean the pre-line frames if that pre-line frame_dict didn't contain
                    # frames that are early in the lap (meaning it wasnt a full lap)
                    frame_dict_sorted_by_distance = sorted(self.frame_dict.copy().items(), key=lambda kv: kv[KEY_INDEX_MAP["lap_distance"]])
                    first_frame_distance_frame, first_frame_distance_values = frame_dict_sorted_by_distance[0]
                    first_frame_distance_value = first_frame_distance_values[KEY_INDEX_MAP["lap_distance"]] or 0
                    if self.session_type not in self.SESSION_TYPES_WITHOUT_OUTLAP and first_frame_distance_value < self.MAX_DISTANCE_COUNT_AS_NEW_LAP:
                        log.info("Assuming an outlap started based on distance delta - killing all new frames (current distance %s, last distance %s, first frame distance %s)" % \
                            (current_distance, self.last_lap_distance, first_frame_distance_value))
                        self.remove_frame(frame_number)
                        # Important to return here to not set the last_lap_distance to the current_distance
                        return
                    else:
                        log.info("Assuming a new lap started based on distance delta - killing all old frames (current distance %s, last distance %s, first frame distance %s)" % \
                            (current_distance, self.last_lap_distance, first_frame_distance_value))
                        self.frame_dict = {frame_number: frame}
        
        # Set the last distance value for future frames
        self.last_lap_distance = current_distance

    def remove_frame(self, frame_number):
        self.frame_dict.pop(frame_number)
        self.frames_popped_list.append(frame_number)

    def process_flashback_event(self, frame_id_flashed_back_to):
        current_frame_max = max(self.frame_dict) if self.frame_dict else None
        deleted_frame_count = 0
        for frame_id, frame_value in self.frame_dict.copy().items():
            if frame_id >= frame_id_flashed_back_to:
                deleted_frame_count += 1
                self.frame_dict.pop(frame_id)
        # Reset last lap distance
        self.last_lap_distance = None
        log.info("Removed frames that were flashbacked away (flbk to %s; max was %s; deleted %s)" % (
            frame_id_flashed_back_to,
            current_frame_max,
            deleted_frame_count
            ))


class TelemetryBase:
    """
    Telemetry data of one or several laps
    """
    TelemetryLapModel = TelemetryLapBase

    def __init__(self, session_type=None):
        self.current_lap_number = None
        self.lap_dict = {}
        self.session_type = session_type

    @property
    def current_lap(self):
        return self.lap_dict.get(self.current_lap_number)

    def frame(self, frame_number):
        if not self.current_lap:
            log.debug("Attempted to get/set a telemetry frame without a current lap")
            return None
        frame_dict = self.current_lap.frame_dict
        if frame_number not in frame_dict:
            frame_dict[frame_number] = []
            for i in range(0, len(KEY_INDEX_MAP)):
                frame_dict[frame_number].append(None)
        return frame_dict[frame_number]

    def set(self, frame_number, **kwargs):
        frame = self.frame(frame_number)
        if frame is None:
            return None
        for key, value in kwargs.items():
            frame_index    = KEY_INDEX_MAP[key]
            decimal_points = KEY_ROUND_MAP[key]
            frame[frame_index] = round(value, decimal_points)
        self.current_lap.clean_frame(frame_number)

    def get_telemetry_api_dict(self, lap_number):
        telemetry_lap = self.lap_dict.get(lap_number)
        if telemetry_lap:
            return telemetry_lap.frame_dict
        return None

    def start_new_lap(self, number):
        """ New lap started in game """
        log.info("Telemetry: start new lap %s" % number)
        if number in self.lap_dict.keys():
            log.info("TelemetryLap number %s already started" % number)
            return None
        # Update current lap number and add to dict
        self.current_lap_number = number
        self.lap_dict[number] = self.TelemetryLapModel(number, session_type=self.session_type)
        # Remove all laps that are not current or last
        if len(self.lap_dict) > 2:
            for key in list(self.lap_dict):
                if key != number and key != (number-1):
                    self.lap_dict.pop(key, None)
                    log.info("Telemetry: deleted telemetry of lap %s" % key)

    def process_flashback_event(self, frame_id_flashed_back_to):
        self.current_lap.process_flashback_event(frame_id_flashed_back_to)
    
    def drop_lap(self, lap_number):
        """ Drop all frames from current lap, if it exists """
        if self.lap_dict.get(lap_number):
            self.current_lap_number = lap_number
            self.lap_dict[lap_number] = self.TelemetryLapModel(lap_number, session_type=self.session_type)
            log.info("Telemetry: dropped telemetry of lap %s" % lap_number)
