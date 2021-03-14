from lib.logger import log
from lib.file_handler import get_path_executable_parent
import json

class Telemetry:
    """
    Stores current telemetry data in memory.
    """
    def __init__(self):
        self.current_lap = None

    def frame(self, frame_number):
        if not self.current_lap:
            log.warning("Attempted to get/set a telemetry frame without a current lap")
            return None
        frame_dict = self.current_lap.frame_dict
        if frame_number not in frame_dict:
            frame_dict[frame_number] = {}
        return frame_dict[frame_number]

    def set(self, frame_number, **kwargs):
        frame = self.frame(frame_number)
        if frame is None:
            return None
        for key, value in kwargs.items():
            if key in frame and frame[key] is not None:
                continue
            else:
                frame[key] = value
        self.current_lap.update_distance_dict(frame_number)

    def start_new_lap(self, number):
        """ New lap started in game """
        if self.current_lap and number == self.current_lap.number:
            log.info("TelemetryLap number %s already started" % number)
            return None
        if self.current_lap:
            self.current_lap.complete()
        self.current_lap = TelemetryLap(number)


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

        # DICTS
        # frame_dict = keyed by frame id
        # distance_dict = keyed by lap distance
        self.frame_dict = {}
        self.distance_dict = {}

        # Constants
        self.MAX_FRAME_GO_BACK_NUMBER = 10

    def update_distance_dict(self, frame_number):
        this_frame = self.frame_dict.get(frame_number)
        if not this_frame:
            return
        if this_frame.get("lap_distance") and this_frame["lap_distance"] > 0:
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
        self.clean_up_flashbacks(frame_number)

    def clean_up_flashbacks(self, frame_number):
        """
        A flashback keeps increasing frames, but sets lap_distance back
        This messes up charts that are distance-indexed
        When a user goes back in lap distance, we delete all "reverted" distance values
        """
        test_last_frame_number = frame_number
        last_frame_number_found = None
        for i in range(1, self.MAX_FRAME_GO_BACK_NUMBER):
            test_last_frame_number = test_last_frame_number - 1
            if test_last_frame_number in self.frame_dict \
               and self.frame_dict[test_last_frame_number].get("lap_distance"):
                last_frame_number_found = test_last_frame_number
                break
        if not last_frame_number_found:
            return
        last_distance_value = self.frame_dict[last_frame_number_found]["lap_distance"]
        current_distance_value = self.frame_dict[frame_number]["lap_distance"]
        if current_distance_value < last_distance_value:
            for key in list(self.distance_dict):
                if key > current_distance_value:
                    self.distance_dict.pop(key, None)

    def complete(self):
        """ Wrap up this lap """
        if self.is_complete_lap():
            #self.process_in_f1laps()
            self.process_in_file_temp()
        return True

    def is_complete_lap(self):
        return len(self.distance_dict) > 1000

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

    def process_in_f1laps(self):
        """ Send complete data to F1Laps """
        pass
