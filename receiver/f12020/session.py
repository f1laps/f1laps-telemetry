import json
import f1_2020_telemetry.types

from receiver.session_base import SessionBase
from receiver.f12020.api import F1LapsAPI
from receiver.f12020.telemetry import Telemetry
from lib.logger import log


class Session(SessionBase):
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
        self.telemetry = Telemetry()

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

    def process_lap_in_f1laps(self, lap_number=None):
        """
        Send Lap to F1Laps; either as a standalone lap or as a session lap,
        depending on game mode
        """
        if self.session_type_supported_by_f1laps_as_session():
            # Create or update full Session object in F1Laps
            return self.create_or_update_session_in_f1laps()
        else:
            # Create only Lap object in F1Laps
            return self.create_lap_in_f1laps(lap_number)

    def create_lap_in_f1laps(self, lap_number):
        """ Send Lap to F1Laps """
        response = F1LapsAPI(self.f1laps_api_key, "f12020").lap_create(
                        track_id              = self.track_id,
                        team_id               = self.team_id,
                        conditions            = self.map_weather_ids_to_f1laps_token(),
                        game_mode             = "time_trial", # hardcoded as the only supported value
                        sector_1_time         = self.lap_list[lap_number]["sector_1_time_ms"],
                        sector_2_time         = self.lap_list[lap_number]["sector_2_time_ms"],
                        sector_3_time         = self.lap_list[lap_number]["sector_3_time_ms"],
                        setup_data            = self.setup,
                        is_valid              = self.lap_list[lap_number].get("is_valid", True),
                        telemetry_data_string = self.get_lap_telemetry_data(lap_number)
                    )
        if response and response.status_code == 201:
            log.info("Lap #%s successfully created in F1Laps" % lap_number)
            return True
        else:
            log.error("Error creating lap %s in F1Laps" % lap_number)
            log.error("F1Laps API response: %s" % json.loads(response.content))
            return False

    def create_or_update_session_in_f1laps(self):
        log.info("Updating session (%s) in F1Laps" % self.map_udp_session_id_to_f1laps_token())
        success,self.f1_laps_session_id = F1LapsAPI(self.f1laps_api_key, "f12020").session_create_or_update(
                    f1laps_session_id = self.f1_laps_session_id,
                    track_id          = self.track_id,
                    team_id           = self.team_id,
                    session_uid       = self.session_udp_uid,
                    conditions        = self.map_weather_ids_to_f1laps_token(),
                    session_type      = self.map_udp_session_id_to_f1laps_token(),
                    finish_position   = self.finish_position,
                    points            = self.points,
                    result_status     = self.result_status, 
                    lap_times         = self.get_f1laps_lap_times_list(),
                    setup_data        = self.setup,
                    is_online_game    = self.is_online_game
                )
        if success:
            log.info("Session (%s) successfully updated in F1Laps" % self.map_udp_session_id_to_f1laps_token())
            return True
        else:
            log.info("Session not updated in F1Laps")
            return False

    def map_udp_session_id_to_f1laps_token(self):
        session_mapping = {
            1: "practice_1",
            2: "practice_2",
            3: "practice_3",
            4: "practice_1", # short practice
            5: "qualifying_1", # q1
            6: "qualifying_2", # q2
            7: "qualifying_3", # q3
            8: "qualifying", # short q
            9: "qualifying", # osq
            10: "race",
            11: "race",
            12: "time_trial",
        }
        return session_mapping.get(self.session_type)

    def session_type_supported_by_f1laps_as_session(self):
        return True if self.session_type and self.session_type != 12 else False

    def get_f1laps_lap_times_list(self):
        lap_times = []
        for lap_number, lap_object in self.lap_list.items():
            if lap_object['sector_1_time_ms'] and lap_object['sector_2_time_ms'] and lap_object['sector_3_time_ms']:
                lap_times.append({
                        "lap_number"           : lap_number,
                        "sector_1_time_ms"     : lap_object['sector_1_time_ms'],
                        "sector_2_time_ms"     : lap_object['sector_2_time_ms'],
                        "sector_3_time_ms"     : lap_object['sector_3_time_ms'],
                        "car_race_position"    : lap_object['car_race_position'],
                        "pit_status"           : lap_object['pit_status'],
                        "tyre_compound_visual" : lap_object.get('tyre_compound_visual'),
                        "telemetry_data_string": self.get_lap_telemetry_data(lap_number)
                    })
        return lap_times

    def get_track_name(self):
        return f1_2020_telemetry.types.TrackIDs.get(self.track_id)


