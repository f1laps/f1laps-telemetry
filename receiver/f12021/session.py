import json

from lib.logger import log
from receiver.session_base import SessionBase
from .types import SessionType, Track
from .api import F1LapsAPI2021


class F12021Session(SessionBase):
    """
    Handles all session-specific variables and logic
    """
    def __init__(self, session_uid):
        # Meta
        self.f1laps_api_key = None
        self.telemetry_enabled = True
        self.game_version = "f12021"
        
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
        self.post_process(lap_number)

    def post_process(self, lap_number):
        log.info("Completed lap #%s" % lap_number)
        if self.lap_should_be_sent_to_f1laps(lap_number):
            if self.lap_should_be_sent_as_session():
                self.send_session_to_f1laps()
            else:
                self.send_lap_to_f1laps(lap_number)

    def lap_should_be_sent_to_f1laps(self, lap_number):
        lap = self.lap_list.get(lap_number)
        if not lap:
            return False
        return bool(lap.get('sector_1_ms') and lap.get('sector_2_ms') and lap.get('sector_3_ms'))

    def lap_should_be_sent_as_session(self):
        return bool(self.session_type and self.get_session_type() != 'time_trial')

    def send_lap_to_f1laps(self, lap_number):
        api = F1LapsAPI2021(self.f1laps_api_key, self.game_version)
        response = api.lap_create(
            track_id              = self.track_id,
            team_id               = self.team_id,
            conditions            = self.map_weather_ids_to_f1laps_token(),
            game_mode             = "time_trial",
            sector_1_time         = self.lap_list[lap_number]["sector_1_ms"],
            sector_2_time         = self.lap_list[lap_number]["sector_2_ms"],
            sector_3_time         = self.lap_list[lap_number]["sector_3_ms"],
            setup_data            = self.setup,
            is_valid              = self.lap_list[lap_number].get("is_valid", True),
            telemetry_data_string = None#self.get_lap_telemetry_data(lap_number)
        )
        if response.status_code == 201:
            log.info("Lap #%s successfully created in F1Laps" % lap_number)
        else:
            log.error("Error creating lap %s in F1Laps: %s" % (lap_number, json.loads(response.content)))

    def send_session_to_f1laps(self):
        api = F1LapsAPI2021(self.f1laps_api_key, self.game_version)
        success, self.f1_laps_session_id = api.session_create_or_update(
            f1laps_session_id = self.f1_laps_session_id,
            track_id          = self.track_id,
            team_id           = self.team_id,
            session_uid       = self.session_udp_uid,
            conditions        = self.map_weather_ids_to_f1laps_token(),
            session_type      = self.get_session_type(),
            finish_position   = self.finish_position,
            points            = self.points,
            result_status     = self.result_status, 
            lap_times         = self.get_f1laps_lap_times_list(),
            setup_data        = self.setup,
            is_online_game    = self.is_online_game
        )
        if success:
            log.info("Session successfully updated in F1Laps")
        else:
            log.info("Session not updated in F1Laps")

    def get_f1laps_lap_times_list(self):
        lap_times = []
        for lap_number, lap_object in self.lap_list.items():
            if lap_object['sector_1_ms'] and lap_object['sector_2_ms'] and lap_object['sector_3_ms']:
                lap_times.append({
                        "lap_number"           : lap_number,
                        "sector_1_time_ms"     : lap_object['sector_1_ms'],
                        "sector_2_time_ms"     : lap_object['sector_2_ms'],
                        "sector_3_time_ms"     : lap_object['sector_3_ms'],
                        "car_race_position"    : lap_object['car_race_position'],
                        "pit_status"           : lap_object['pit_status'],
                        "tyre_compound_visual" : lap_object.get('tyre_compound_visual'),
                        "telemetry_data_string": None#self.get_lap_telemetry_data(lap_number)
                    })
        return lap_times



