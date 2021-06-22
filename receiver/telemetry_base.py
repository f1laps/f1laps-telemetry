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

class TelemetryBase:
    """
    Telemetry data of one or several laps
    """
    TelemetryLapModel = TelemetryLapBase

    def __init__(self):
        self.current_lap_number = None
        self.lap_dict = {}

    @property
    def current_lap(self):
        return self.lap_dict.get(self.current_lap_number)

    def frame(self, frame_number):
        if not self.current_lap:
            log.warning("Attempted to get/set a telemetry frame without a current lap")
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
        log.info("Start new lap %s" % number)
        if self.current_lap_number and number == self.current_lap_number:
            log.info("TelemetryLap number %s already started" % number)
            return None
        # Update current lap number and add to dict
        self.current_lap_number = number
        self.lap_dict[number] = self.TelemetryLapModel(number)
        # Remove all laps that are not current or last
        if len(self.lap_dict) > 2:
            for key in list(self.lap_dict):
                if key != number and key != (number-1):
                    self.lap_dict.pop(key, None)
                    log.debug("Deleted telemetry of lap %s" % key)


class TelemetryLapBase:
    """
    Stores current lap telemetry data in memory
    """

    def __init__(self, number):
        # Current lap number
        self.number = number

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
        if frame[KEY_INDEX_MAP["lap_distance"]]:
            current_distance = frame[KEY_INDEX_MAP["lap_distance"]]
            if not current_distance:
                return

            if not isinstance(current_distance, float) and not isinstance(current_distance, int):
                return

            # Delete frames that are pre session FIRST LINE CROSS start
            if current_distance < 0:
                self.frame_dict.pop(frame_number)
                self.frames_popped_list.append(frame_number)
                return

            # If we have current and last lap distance, check that we're incrementing the distance
            elif self.last_lap_distance:    
                # Check if last distance was higher - this means something UNEXPECTED happened
                if self.last_lap_distance > current_distance:

                    # First, if current distance is SLIGHTLY less than last distance, we assume its a FLASHBACK
                    # We pop any frame that has a greater distance
                    if (self.last_lap_distance - current_distance) < self.MAX_FLASHBACK_DISTANCE_METERS:
                        log.info("Assuming a flashback happened - deleting all future frames")
                        for frame_key, frame_value in self.frame_dict.copy().items():
                            if frame_value[KEY_INDEX_MAP["lap_distance"]]\
                             and frame_value[KEY_INDEX_MAP["lap_distance"]] >= current_distance\
                             and frame_key != frame_number:
                                self.frame_dict.pop(frame_key)

                    # There's another case: we came out of the garage, which doesnt increment the lap counter (weird!)
                    # And lap distance pre line cross is NOT negative (also weird!)
                    # So if we drop the current distance down to a super small number, we assume a NEW LAP was started
                    elif current_distance < self.MAX_DISTANCE_COUNT_AS_NEW_LAP:
                        log.info("Assuming a new lap started based on distance delta - killing all old frames")
                        self.frame_dict = {frame_number: frame}
        
        # Set the last distance value for future frames
        self.last_lap_distance = current_distance
        #log.info("Frame %s: last distance %s | CD %s" % (frame_number, self.last_lap_distance, current_distance))
