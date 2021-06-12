import json

from lib.logger import log


class F12021Session:
    """
    Handles all session-specific variables and logic
    """
    def __init__(self, session_uid):
        ###################################################
        # Attributes set on Session start
        ###################################################
        self.session_udp_uid = session_uid
        self.track_id = None
        self.session_type = None
        self.weather_ids = []
        self.f1laps_api_key = None
        self.telemetry_enabled = True
        self.is_online_game = False

        ###################################################
        # Attributes set with participants packet once
        ###################################################
        self.team_id = None

        ###################################################
        # Attributes set with each lap
        ###################################################
        self.lap_list = {}
        self.lap_number_current = None

        ###################################################
        # Attributes set with the setup package
        ###################################################
        self.setup = {}

        ###################################################
        # Attributes set with the telemetry package
        ###################################################
        self.telemetry = None#Telemetry()

        ###################################################
        # Attributes set with the final classification
        ###################################################
        self.finish_position = None
        self.result_status = None
        self.points = None

        ###################################################
        # Attributes set via F1Laps API
        ###################################################
        self.f1_laps_session_id = None

    def get_track_name(self):
        raise Exception("Not implemented yet")

    def get_session_type(self):
        raise Exception("Not implemented yet")

    def get_lap_telemetry_data(self, lap_number):
        if self.telemetry_enabled:
            telemetry_data = self.telemetry.get_telemetry_api_dict(lap_number)
            if telemetry_data:
                return json.dumps(telemetry_data)
        return None


