import json
import f1_2020_telemetry.types

from receiver.f1laps import F1LapsAPI
from receiver.telemetry import Telemetry
from lib.logger import log


class Session:
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
        log.info("Sending lap %s to F1Laps" % lap_number)
        response = F1LapsAPI(self.f1laps_api_key).lap_create(
                        track_id       = self.track_id,
                        team_id        = self.team_id,
                        conditions     = self.map_weather_ids_to_f1laps_token(),
                        game_mode      = "time_trial", # hardcoded as the only supported value
                        sector_1_time  = self.lap_list[lap_number]["sector_1_time_ms"],
                        sector_2_time  = self.lap_list[lap_number]["sector_2_time_ms"],
                        sector_3_time  = self.lap_list[lap_number]["sector_3_time_ms"],
                        setup_data     = self.setup,
                        telemetry_data = self.telemetry.get_telemetry_api_dict(lap_number)
                    )
        if response.status_code == 201:
            log.info("Lap #%s successfully created in F1Laps" % lap_number)
            return True
        else:
            log.error("Error creating lap %s in F1Laps" % lap_number)
            log.error("F1Laps API response: %s" % json.loads(response.content))
            return False

    def create_or_update_session_in_f1laps(self):
        if self.f1_laps_session_id:
            return self.update_session_in_f1laps()
        else:
            return self.create_session_in_f1laps()

    def create_session_in_f1laps(self):
        """
        Create new Session in F1Laps 
        Also attempts to retrieve & update Session if already created previously
        """
        log.info("Creating full session (%s) in F1Laps" % self.map_udp_session_id_to_f1laps_token())
        response = F1LapsAPI(self.f1laps_api_key).session_create(
                        track_id        = self.track_id,
                        team_id         = self.team_id,
                        session_uid     = self.session_udp_uid,
                        conditions      = self.map_weather_ids_to_f1laps_token(),
                        session_type    = self.map_udp_session_id_to_f1laps_token(),
                        finish_position = self.finish_position,
                        points          = self.points,
                        result_status   = self.result_status, 
                        lap_times       = self.get_f1laps_lap_times_list(),
                        setup_data      = self.setup
                    )
        if response.status_code == 201:
            log.info("Session (%s) successfully created in F1Laps" % self.map_udp_session_id_to_f1laps_token())
            self.f1_laps_session_id = json.loads(response.content)['id']
            return True
        else:
            # The call may have failed because this session was already posted to F1Laps
            # But we haven't stored the ID locally (e.g. when user restarts script during a session)
            # We'll try to get the F1Laps ID via GET list call, then try again
            if response.status_code == 403 and not self.f1_laps_session_id:
                retrieved_f1_laps_session_id = self.retrieve_f1laps_session_id()
                if retrieved_f1_laps_session_id:
                    self.f1_laps_session_id = retrieved_f1_laps_session_id
                    return self.update_session_in_f1laps()
                else:
                    log.error("Session can't be created, and no existing session found in F1Laps.")
                    return False
            else:
                log.error("Error creating session (%s) in F1Laps" % self.map_udp_session_id_to_f1laps_token())
                log.error("F1Laps API response: %s" % json.loads(response.content))
                return False

    def update_session_in_f1laps(self):
        """ Update existing Session in F1Laps """
        log.info("Updating full session (%s) in F1Laps" % self.map_udp_session_id_to_f1laps_token())
        response = F1LapsAPI(self.f1laps_api_key).session_update(
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
                    setup_data        = self.setup
                )
        if response.status_code == 200:
            log.info("Session (%s) successfully updated in F1Laps" % self.map_udp_session_id_to_f1laps_token())
            return True
        else:
            log.error("Error updating session (%s) in F1Laps" % self.map_udp_session_id_to_f1laps_token())
            log.error("F1Laps API response: %s" % json.loads(response.content))
            return False

    def retrieve_f1laps_session_id(self):
        """ Try to retrieve previous session id from F1Laps """
        log.debug("Trying to retrieve F1Laps session id for UDP session id %s" % self.session_udp_uid)
        # List all sessions from F1Laps
        list_response = self.list_sessions_in_f1laps()
        list_response_content = json.loads(list_response.content)
        if list_response_content['results'] and len(list_response_content['results']) == 1:
            f1laps_session_id = list_response_content['results'][0]['id']
            log.debug("Found existing session id %s in F1Laps" % f1laps_session_id)
            return f1laps_session_id
        else:
            log.debug("No session found in F1Laps")
            return False

    def list_sessions_in_f1laps(self):
        """ List Sessions in F1Laps, filtered by UDP session id"""
        log.debug("Searching sessions for ID %s in F1Laps" % self.session_udp_uid)
        return F1LapsAPI(self.f1laps_api_key).session_list(self.session_udp_uid)

    def map_udp_session_id_to_f1laps_token(self):
        session_mapping = {
            1: "practice_1",
            2: "practice_2",
            3: "practice_3",
            4: "practice_1", # short practice
            5: "qualifying",
            6: "qualifying",
            7: "qualifying",
            8: "qualifying",
            9: "qualifying",
            10: "race",
            11: "race",
            12: "time_trial",
        }
        return session_mapping.get(self.session_type)

    def session_type_supported_by_f1laps_as_session(self):
        return True if self.session_type and self.session_type != 12 else False

    def map_weather_ids_to_f1laps_token(self):
        """
        Map UDP weather IDs to F1Laps weather token
        0-2: dry; 3-5: wet; both: mixed
        """
        has_dry_weather = any(x in self.weather_ids for x in [0, 1, 2])
        has_wet_weather = any(x in self.weather_ids for x in [3, 4, 5])
        if has_dry_weather and has_wet_weather:
            return 'mixed'
        else:
            return 'wet' if has_wet_weather else 'dry'

    def get_f1laps_lap_times_list(self):
        lap_times = []
        for lap_number, lap_object in self.lap_list.items():
            if lap_object['sector_1_time_ms'] and lap_object['sector_2_time_ms'] and lap_object['sector_3_time_ms']:
                lap_times.append({
                        "lap_number"          : lap_number,
                        "sector_1_time_ms"    : lap_object['sector_1_time_ms'],
                        "sector_2_time_ms"    : lap_object['sector_2_time_ms'],
                        "sector_3_time_ms"    : lap_object['sector_3_time_ms'],
                        "car_race_position"   : lap_object['car_race_position'],
                        "pit_status"          : lap_object['pit_status'],
                        "tyre_compound_visual": lap_object.get('tyre_compound_visual'),
                        "telemetry_data"      : self.telemetry.get_telemetry_api_dict(lap_number)
                    })
        return lap_times

    def get_track_name(self):
        return f1_2020_telemetry.types.TrackIDs.get(self.track_id)



