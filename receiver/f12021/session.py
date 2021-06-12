import json

from lib.logger import log
from .types import SessionType, Track


class F12021Session:
    """
    Handles all session-specific variables and logic
    """
    def __init__(self, session_uid):
        # Meta
        self.f1laps_api_key = None
        self.telemetry_enabled = True
        
        # Session
        self.session_udp_uid = session_uid
        self.session_type = None
        self.track_id = None
        self.team_id = None
        self.is_online_game = False
        self.ai_difficulty = None
        self.weather_ids = []

        # Laps
        self.lap_list = {}

        # Setup 
        self.setup = {}

        # Telemetry
        self.telemetry = None#Telemetry()

        # Final classification
        self.finish_position = None
        self.result_status = None
        self.points = None

        # Data we get from F1Laps
        self.f1_laps_session_id = None

    def start(self):
        log.info("*************************************************")
        log.info("New session started: %s %s (ID %s)" % (self.get_track_name(), 
                                                         self.get_session_type(),
                                                         self.session_udp_uid))
        log.info("*************************************************")

    def get_track_name(self):
        return Track.get(self.track_id)

    def get_session_type(self):
        return SessionType.get(self.session_type)

    def complete_lap(self, lap_number, sector_1_ms, sector_2_ms, sector_3_ms, tyre_visual):
        if not self.lap_list.get(lap_number):
            self.lap_list[lap_number] = {}
        self.lap_list[lap_number]['lap_number']  = lap_number
        self.lap_list[lap_number]['sector_1_ms'] = sector_1_ms
        self.lap_list[lap_number]['sector_2_ms'] = sector_2_ms
        self.lap_list[lap_number]['sector_3_ms'] = sector_3_ms
        self.lap_list[lap_number]['tyre_compound_visual'] = tyre_visual
        self.push_lap_to_f1laps(lap_number)

    def push_lap_to_f1laps(self, lap_number):
        # verify that its complete - like has S1 & S2 & S3 > 1000 or so
        pass

    def get_lap_telemetry_data(self, lap_number):
        if self.telemetry_enabled:
            telemetry_data = self.telemetry.get_telemetry_api_dict(lap_number)
            if telemetry_data:
                return json.dumps(telemetry_data)
        return None


