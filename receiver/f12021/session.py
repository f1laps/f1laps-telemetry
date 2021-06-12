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
        self.lap_number_current = None

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

    def get_lap_telemetry_data(self, lap_number):
        if self.telemetry_enabled:
            telemetry_data = self.telemetry.get_telemetry_api_dict(lap_number)
            if telemetry_data:
                return json.dumps(telemetry_data)
        return None


