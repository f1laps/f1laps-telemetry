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
        #log.info(self.current_lap.frame_dict)

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
        self.number = number
        self.frame_dict = {}

    def complete(self):
        """ Wrap up this lap """
        #has_all_necessary_data = ?
        if False:#has_all_necessary_data:
            self.process_in_f1laps()
        log.info("---------------------------------------------------------------------")
        log.info("---------------------------------------------------------------------")
        log.info("---------------------------------------------------------------------")
        log.info("Completed lap %s with frame dict:" % self.number)
        #log.info(self.frame_dict)
        try:
            file_name = "telemetry_dump_test1_lap%s.txt" % self.number
            with open(get_path_executable_parent(file_name), 'w+') as f: 
                f.write(json.dumps(self.frame_dict))
            log.info("Wrote to file %s" % file_name)
        except Exception as ex:
            log.info("Could not write to config file: %s" % ex)
        return True

    def process_in_f1laps(self):
        """ Send complete data to F1Laps """
        log.info()
