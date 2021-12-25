import json

from lib.logger import log
from receiver.session_base import SessionBase, ParticipantBase
from .types import SessionType, Track
from .api import F1LapsAPI2021
from .telemetry import F12021Telemetry


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
        self.current_lap_in_outlap_logging_status = False

        # Setup 
        self.setup = {}

        # Telemetry
        self.telemetry = F12021Telemetry()

        # Final classification
        self.participants = []
        self.finish_position = None
        self.result_status = None
        self.points = None

        # Data we get from F1Laps
        self.f1_laps_session_id = None

        # Enable for motion packet / minimap
        # self.last_logged_distance = None
        # self.lap_distance = None

    def start(self):
        log.info("*************************************************")
        log.info("New session started: %s %s (ID %s)" % (self.get_track_name(), 
                                                         self.get_session_type(),
                                                         self.session_udp_uid))
        log.info("*************************************************")

    def set_session_type(self, session_type):
        self.session_type = session_type
        self.telemetry.session_type = session_type

    def get_track_name(self):
        return Track.get(self.track_id)

    def get_session_type(self):
        return SessionType.get(self.session_type)

    def start_new_lap(self, lap_number):
        """ 
        As set by the Lap packet, this method is called 
        when the currentLap number was increased 
        """
        log.info("Session (via Lap packet): start new lap %s" % lap_number)
        # Add new lap to lap list
        self.lap_list[lap_number] = {}
        # Update telemetry
        self.telemetry.start_new_lap(lap_number)

    def complete_lap_v2(self, lap_number):
        """ 
        This is meant to be a temporary function as it's now based on the Lap packet again
        The Session History packet turned out to be too buggy, which is why the original complete_lap
        isn't used currently anymore.
        """
        log.info("Session (via Lap packet): complete lap %s" % lap_number)
        self.post_process(lap_number)

    def post_process(self, lap_number):
        # Send to F1Laps
        if self.lap_should_be_sent_to_f1laps(lap_number):
            log.info("Session: post process lap %s" % lap_number)
            if self.lap_should_be_sent_as_session():
                self.send_session_to_f1laps()
            else:
                self.send_lap_to_f1laps(lap_number)

    def complete_session(self):
        log.info("Session: complete session")
        self.send_session_to_f1laps()

    def lap_should_be_sent_to_f1laps(self, lap_number):
        lap = self.lap_list.get(lap_number)
        lap_f1laps_status_key = "has_been_sent_to_f1laps"
        if not lap:
            log.info("Not sending lap #%s to F1Laps because it doesn't exist" % lap_number)
            return False
        if not bool(lap.get('sector_1_ms') and lap.get('sector_2_ms') and lap.get('sector_3_ms')):
            log.info("Not sending lap #%s to F1Laps because it doesn't have non-zero values for all sectors" % lap_number)
            return False
        if lap.get(lap_f1laps_status_key):
            log.debug("Not sending lap #%s to F1Laps because it has already been posted" % lap_number)
            return False
        # Mark this session as "already sent to F1Laps, don't send again"
        lap[lap_f1laps_status_key] = True
        return True

    def lap_should_be_sent_as_session(self):
        return bool(self.session_type and self.get_session_type() != 'time_trial')

    def is_valid_for_f1laps(self):
        if self.session_type is None:
            log.warning("Attempted to send session to F1Laps without session type: %s" % self)
            return False
        if self.team_id is None:
            log.warning("Attempted to send session to F1Laps without team ID: %s" % self)
            return False
        return True

    def send_lap_to_f1laps(self, lap_number):
        if not self.is_valid_for_f1laps():
            return 
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
            telemetry_data_string = self.get_lap_telemetry_data(lap_number)
        )
        if response is None:
            log.info("API call failed - lap not created in F1Laps")
        elif response.status_code == 201:
            log.info("Lap #%s successfully created in F1Laps" % lap_number)
        else:
            log.error("Error creating lap %s in F1Laps: %s" % (lap_number, json.loads(response.content)))

    def send_session_to_f1laps(self):
        if not self.is_valid_for_f1laps():
            return 
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
            is_online_game    = self.is_online_game,
            ai_difficulty     = self.ai_difficulty or None,
            classifications   = self.get_classification_list()
        )
        if success:
            log.info("Session successfully updated in F1Laps")
        else:
            log.info("Session not updated in F1Laps")

    def get_f1laps_lap_times_list(self):
        lap_times = []
        for lap_number, lap_object in self.lap_list.items():
            if lap_object.get('sector_1_ms') and lap_object.get('sector_2_ms') and lap_object.get('sector_3_ms'):
                lap_times.append({
                        "lap_number"           : lap_number,
                        "sector_1_time_ms"     : lap_object['sector_1_ms'],
                        "sector_2_time_ms"     : lap_object['sector_2_ms'],
                        "sector_3_time_ms"     : lap_object['sector_3_ms'],
                        "car_race_position"    : lap_object.get('car_race_position'),
                        "pit_status"           : lap_object.get('pit_status'),
                        "tyre_compound_visual" : lap_object.get('tyre_compound_visual'),
                        "telemetry_data_string": self.get_lap_telemetry_data(lap_number)
                    })
        return lap_times

    def get_classification_list(self):
        if not self.has_final_classification():
            return []
        classifications = []
        for participant in self.participants:
            classifications.append({
                "driver": participant.driver,
                "driver_index": participant.driver_index,
                "team": participant.team,
                "result_status": participant.result_status,
                "points": participant.points or None,
                "finish_position": participant.finish_position or None,
                "grid_position": participant.grid_position,
                "lap_time_best": participant.lap_time_best or None,
                "race_time_total": participant.race_time_total or None,
                "penalties_time_total": participant.penalties_time_total or None,
                "penalties_number": participant.penalties_number
            })
        return classifications

    def has_final_classification(self):
        has_user_classification = bool(self.result_status)
        if has_user_classification:
            return True
        participants_count = len(self.participants)
        if not participants_count:
            return False
        last_participant = self.participants[participants_count-1]
        return bool(last_participant.result_status)

    def is_time_trial(self):
        return self.session_type in [13]

    def is_race(self):
        return self.session_type in [10, 11, 12]

    def is_qualifying_non_one_shot(self):
        return self.session_type in [5, 6, 7, 8]

    def is_qualifying_one_shot(self):
        return self.session_type in [9]

    def add_participant(self, **kwargs):
        participant = ParticipantBase(**kwargs)
        self.participants.append(participant)
        log.debug("Added Participant: %s" % participant)

    def complete_lap(self, lap_number, sector_1_ms, sector_2_ms, sector_3_ms, tyre_visual):
        """ 
        While this method is similar to new_lap_started, it's different
        It's not called as soon as possible, but when all previous lap data is available
        There might be a ~1 second gap after the line is crossed

        As set by the SessionHistory packet, this method is called 
        when the previous lap data was published in the history packet
        """
        # Temp hack: there is a bug in the telemetry that the SessionHistory gets sent with 
        # laps from the last session. This prevents the telemetry from being started by
        # our lap packet. So we start it here too. 
        # Remove this once the bug is fixed
        self.telemetry.start_new_lap(lap_number)
        log.info("Session (via History packet): complete lap %s" % lap_number)
        if not self.lap_list.get(lap_number):
            self.lap_list[lap_number] = {}
        self.lap_list[lap_number]['lap_number']  = lap_number
        self.lap_list[lap_number]['sector_1_ms'] = sector_1_ms
        self.lap_list[lap_number]['sector_2_ms'] = sector_2_ms
        self.lap_list[lap_number]['sector_3_ms'] = sector_3_ms
        self.lap_list[lap_number]['tyre_compound_visual'] = tyre_visual
        self.post_process(lap_number)


