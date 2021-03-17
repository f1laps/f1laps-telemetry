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
    "stear"       : 6,
    "drs"         : 7,
}

KEY_ROUND_MAP = {
    "lap_distance": 2,
    "lap_time"    : 0,
    "speed"       : 0,
    "brake"       : 3,
    "throttle"    : 3,
    "gear"        : 0,
    "stear"       : 3,
    "drs"         : 0,
}

class Telemetry:
    """
    Stores current telemetry data in memory.
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
        #self.current_lap.update_distance_dict(frame_number)

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
        if self.current_lap:
            self.current_lap.complete()
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
    Stores current lap telemetry data in memory.
    lap_distance        int     0-10000     5 bytes
    lap_time            int     0-200000    6 bytes
    speed               int     0-400       3 bytes
    brake               float   0-1         4 bytes
    throttle            float   0-1         4 bytes
    gear                int     -1-8        1 byte
    steer               float   -1-1        1 byte
    DRS                 int     0/1         1 byte
    """
    def __init__(self, number):
        # Current lap number
        self.number = number

        # Each frame is a key in this dict
        # Each holds a list of the telemetry values
        self.frame_dict = {}

        # DEPRECATE
        #self.frame_dict_clean = {}
        #self.distance_dict = {}

        # Constants
        self.MAX_FRAME_GO_BACK_NUMBER = 10

    def clean_frame(self, frame_number):
        frame = self.frame_dict.get(frame_number)
        if not frame:
            return
        if frame[KEY_INDEX_MAP["lap_distance"]] and frame[KEY_INDEX_MAP["lap_distance"]] < 0:
            # Delete frames that are pre lap start
            self.frame_dict.pop(frame_number)
        self.clean_up_flashbacks(frame_number)

    def clean_up_flashbacks(self, frame_number):
        """
        A flashback keeps increasing frames, but sets lap_distance back
        This messes up charts that are distance-indexed
        When a user goes back in lap distance, we delete all "reverted" frames
        """
        test_last_frame_number = frame_number
        last_frame_number_found = None
        distance_key = KEY_INDEX_MAP["lap_distance"]
        # First find the last frame that has a distance value
        for i in range(1, self.MAX_FRAME_GO_BACK_NUMBER):
            test_last_frame_number = test_last_frame_number - 1
            if test_last_frame_number in self.frame_dict:
                last_frame_number_found = test_last_frame_number
                break
        if not last_frame_number_found:
            return
        # Now check if the distance of the last frame is greater than the current
        # Which implies that the user flashbacked
        last_distance_value = self.frame_dict[last_frame_number_found][distance_key]
        current_distance_value = self.frame_dict[frame_number][distance_key]
        if current_distance_value < last_distance_value:
            # Delete all frames where distance value is greater than current distance
            total_frame_count = len(self.frame_dict)
            decreasing_frame_number = frame_number
            for i in range(1, total_frame_count):
                decreasing_frame_number = decreasing_frame_number - 1
                decreasing_frame = self.frame_dict.get(decreasing_frame_number)
                if decreasing_frame and decreasing_frame[distance_key] >= current_distance_value:
                    self.frame_dict.pop(decreasing_frame_number)
                else:
                    break

    def complete(self):
        """ Wrap up this lap """
        #if self.is_complete_lap():
        #self.process_in_f1laps()
        self.process_in_file_temp()
        #pass
        return True

    def process_in_file_temp(self):
        log.info("---------------------------------------------------------------------")
        log.info("---------------------------------------------------------------------")
        log.info("---------------------------------------------------------------------")
        log.info("Completed lap %s with frame dict:" % self.number)
        try:
            # frames
            file_name = "telemetry_dump_test2_lap%s_frames.txt" % self.number
            with open(get_path_executable_parent(file_name), 'w+') as f: 
                f.write(json.dumps(self.frame_dict))
            log.info("Wrote to file %s" % file_name)
            # distance
            file_name = "telemetry_dump_test2_lap%s_distance.txt" % self.number
            with open(get_path_executable_parent(file_name), 'w+') as f: 
                f.write(json.dumps(self.distance_dict))
            log.info("Wrote to file %s" % file_name)
        except Exception as ex:
            log.info("Could not write to config file: %s" % ex)

    """def update_distance_dict(self, frame_number):
        this_frame = self.frame_dict.get(frame_number)
        if not this_frame:
            return
        
        #### CLEAN FRAME DICT
        self.frame_dict_clean[this_frame] = []
        if not self.frame_dict_clean.get(this_frame):
            self.frame_dict_clean[this_frame] = [None, None, None, None, None, None, None, None]
        fdc = self.frame_dict_clean[this_frame]
        if this_frame.get("lap_time") is not None:
            fdc[0] = round(this_frame["lap_time"], 0)
        if this_frame.get("speed") is not None:
            fdc[1] = this_frame["speed"]
        if this_frame.get("brake") is not None:
            fdc[2] = round(this_frame["brake"], 3)
        if this_frame.get("throttle") is not None:
            fdc[3] = round(this_frame["throttle"], 3)
        if this_frame.get("gear") is not None:
            fdc[4] = this_frame["gear"]
        if this_frame.get("steer") is not None:
            fdc[5] = round(this_frame["steer"], 3)
        if this_frame.get("drs") is not None:
            fdc[6] = this_frame["drs"]
        if this_frame.get("lap_distance") is not None:
            fdc[7] = round(this_frame["lap_distance"], 2)

        #### DISTANCE DICT
        try:
            lap_distance = int(this_frame["lap_distance"])
        except:
            lap_distance = None
        if lap_distance and lap_distance > 0:
            lap_distance = round(this_frame["lap_distance"], 2)
            # order matters since we're not setting keys
            if not self.distance_dict.get(lap_distance):
                self.distance_dict[lap_distance] = [None, None, None, None, None, None, None]
            if this_frame.get("lap_time") is not None:
                self.distance_dict[lap_distance][0] = round(this_frame["lap_time"], 0)
            if this_frame.get("speed") is not None:
                self.distance_dict[lap_distance][1] = this_frame["speed"]
            if this_frame.get("brake") is not None:
                self.distance_dict[lap_distance][2] = round(this_frame["brake"], 3)
            if this_frame.get("throttle") is not None:
                self.distance_dict[lap_distance][3] = round(this_frame["throttle"], 3)
            if this_frame.get("gear") is not None:
                self.distance_dict[lap_distance][4] = this_frame["gear"]
            if this_frame.get("steer") is not None:
                self.distance_dict[lap_distance][5] = round(this_frame["steer"], 3)
            if this_frame.get("drs") is not None:
                self.distance_dict[lap_distance][6] = this_frame["drs"]
        self.clean_up_flashbacks(frame_number)"""