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

class Telemetry:
    """
    Telemetry data of one or several laps
    """
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
        if self.current_lap_number and number == self.current_lap_number:
            log.info("TelemetryLap number %s already started" % number)
            return None
        # Update current lap number and add to dict
        self.current_lap_number = number
        self.lap_dict[number] = TelemetryLap(number)
        # Remove all laps that are not current or last
        if len(self.lap_dict) > 2:
            for key in list(self.lap_dict):
                if key != number and key != (number-1):
                    self.lap_dict.pop(key, None)
                    log.debug("Deleted telemetry of lap %s" % key)


class TelemetryLap:
    """
    Stores current lap telemetry data in memory
    """

    def __init__(self, number):
        # Current lap number
        self.number = number

        # Each frame is a key in this dict
        # Each holds a list of the telemetry values
        self.frame_dict = {}

        # Ensure we're incrementing lap distance
        # If we don't, we need to remove the dict
        self.last_lap_distance = None

    def clean_frame(self, frame_number):
        frame = self.frame_dict.get(frame_number)
        if not frame:
            return
        if frame[KEY_INDEX_MAP["lap_distance"]]:
            current_distance = frame[KEY_INDEX_MAP["lap_distance"]]
            # Delete frames that are pre lap start
            if current_distance < 0:
                self.frame_dict.pop(frame_number)
            elif current_distance and current_distance > 0:
                # Kill frame if distance was decreased
                if self.last_lap_distance and self.last_lap_distance > current_distance:
                    self.frame_dict.pop(frame_number)
                else:
                    self.last_lap_distance = current_distance
