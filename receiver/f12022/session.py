import json
import logging
log = logging.getLogger(__name__)

from receiver.session_base import SessionBase, ParticipantBase
from receiver.f12022.lap import F12022Lap
from receiver.f12022.types import SessionType, Track, map_game_mode_to_f1laps
from receiver.f12022.api import F1LapsAPI2022


class F12022Session(SessionBase):
    """
    A F1 22 game session (i.e. a specific run on a track)
    """
    def __init__(self,
                 f1laps_api_key,
                 telemetry_enabled,
                 session_uid,
                 session_type,
                 track_id,
                 is_online_game,
                 ai_difficulty,
                 weather_id,
                 game_mode,
                 team_id=None,
                ):
        # Meta
        self.f1laps_api_key = f1laps_api_key
        self.telemetry_enabled = telemetry_enabled
        # Game version also defines API base URL
        self.game_version = "f12022"
        
        # Session
        self.session_udp_uid = session_uid
        self.session_type = session_type
        self.track_id = track_id
        self.team_id = team_id
        self.is_online_game = is_online_game
        self.ai_difficulty = ai_difficulty
        self.weather_ids = set([weather_id]) # set() maintains uniqueness
        self.game_mode = self.map_game_mode(game_mode)

        # Laps
        self.lap_list = {}

        # Setup 
        self.setup = {}

        # Final classification
        self.participants = []
        self.finish_position = None
        self.result_status = None
        self.points = None

        # Data we get from F1Laps
        self.f1_laps_session_id = None

        # Log session init
        log.info("*************************************************")
        log.info("New session started: %s %s (ID %s)" % (self.get_track_name(), self.get_session_type(), self.session_udp_uid))
        log.info("*************************************************")
    
    def get_session_type(self):
        return SessionType.get(self.session_type)
    
    def get_track_name(self):
        return Track.get(self.track_id)
    
    def is_time_trial(self):
        """ Called by PenaltyBase """
        return not self.is_multi_lap_session()

    def update_weather(self, weather_id):
        """ Given a new weather_id from the session packet, update the session's weather set """
        self.weather_ids.add(weather_id)
    
    def map_game_mode(self, game_mode):
        """ Map the UDP game_mode value to the F1Laps value """
        return map_game_mode_to_f1laps(game_mode)
    
    def set_team_id(self, team_id):
        """ 
        Set the session's team ID
        We could just do this outside a method, but good to keep it here
        as we also update the game_mode. So let's make it explicit.
        """
        if self.team_id is not None:
            return 
        self.team_id = team_id
        self.update_game_mode_with_team_id()
    
    def update_game_mode_with_team_id(self):
        """ 
        The UDP data game_mode only has "career", it doesn't break out MyTeam vs Driver Career
        Once we have both the game_mode and the team_id, we can pick and update game_mode
        """
        # Team_id needs to be tested against None (not 0, which is a valid value)
        if self.team_id is None or self.game_mode != "career":
            return
        elif self.team_id == 255:
            self.game_mode = "my_team"
        else:
            self.game_mode = "driver_career"
    
    def get_lap(self, lap_number):
        """ 
        Return the Lap object for the given lap_number 
        If it doesn't exist, add it and return it
        Also sync lap - 1
        """
        if lap_number not in self.lap_list:
            # Create new lap
            self.add_lap(lap_number)
            # Finish completed (previous) lap
            self.finish_completed_lap(lap_number - 1)
        return self.lap_list[lap_number]
    
    def get_current_lap(self):
        """ Return the most recent (highest) Lap object in self.lap_list """
        return self.lap_list[max(self.lap_list)] if self.lap_list else None
    
    def add_lap(self, lap_number):
        """ Start a new lap by creating the Lap object and adding it to the lap_list """
        new_lap = F12022Lap(lap_number=lap_number, session_type=self.session_type)
        self.lap_list[lap_number] = new_lap
        return new_lap
    
    def finish_completed_lap(self, lap_number):
        """ Once a lap is completed, finish it """
        return self.sync_to_f1laps(lap_number)

    def can_be_synced_to_f1laps(self):
        """ Check if this session has all required data to be sent to F1Laps """
        return self.team_id is not None and self.session_type
    
    def is_multi_lap_session(self):
        """ Check if this session gets synced as session or individual laps """
        return bool(self.get_session_type() != 'time_trial')
    
    def add_participant(self, participant_data):
        """ Add a driver to a session """
        participant = ParticipantBase(**participant_data)
        self.participants.append(participant)
        return participant

    def sync_to_f1laps(self, lap_number=None, sync_entire_session=False):
        """ Send a lap or session to F1Laps, if it's ready for sync """
        # When we complete individual lap, we are only looking to sync 
        # in the context of that lap completion
        lap = None
        if not sync_entire_session:
            lap = self.lap_list.get(lap_number)
            if not lap:
                log.info("Skipping sync of lap %s, lap not found" % lap_number)
                return
        # For entire session syncs, or for validated individual lap syncs, proceed now
        if (not self.can_be_synced_to_f1laps) or (lap and not lap.can_be_synced_to_f1laps()):
            log.info("Skipping sync of lap %s, not ready for sync" % lap_number)
            return
        # Send lap to F1Laps
        api = F1LapsAPI2022(self.f1laps_api_key, self.game_version)
        if self.is_multi_lap_session():
            # Sync entire session
            success, f1l_session_id = self.sync_session_to_f1laps(api)
            self.f1_laps_session_id = f1l_session_id
        else:
            # Sync individual lap
            success = self.sync_lap_to_f1laps(lap, api)
        return success
    
    def sync_lap_to_f1laps(self, lap, api):
        """ Send individual lap to F1Laps """
        # Mark the lap as synced to F1Laps
        # Technically it depends on the API call, and we should mark it on success only
        # Unclear what the side effects are though 
        lap.has_been_synced_to_f1l = True
        # Send to API
        success = api.lap_create(
            track_id              = self.track_id,
            team_id               = self.team_id,
            conditions            = self.map_weather_ids_to_f1laps_token(),
            # game_mode should always be time_trial
            # instead of hardcoding, we keep it dynamic to debug when needed
            game_mode             = self.game_mode,
            sector_1_time         = lap.sector_1_ms,
            sector_2_time         = lap.sector_2_ms,
            sector_3_time         = lap.sector_3_ms,
            setup_data            = self.setup,
            is_valid              = lap.is_valid,
            telemetry_data_string = self.get_telemetry_string(lap)
        )
        if success:
            log.info("%s successfully synced to F1Laps" % lap)
        else:
            log.info("%s failed sync to F1Laps" % lap)
        return success
    
    def sync_session_to_f1laps(self, api):
        """ Send full sessiom to F1Laps """
        success, f1l_session_id = api.session_create_or_update(
            f1laps_session_id = self.f1_laps_session_id,
            track_id          = self.track_id,
            team_id           = self.team_id,
            session_uid       = self.session_udp_uid,
            conditions        = self.map_weather_ids_to_f1laps_token(),
            session_type      = self.get_session_type(),
            game_mode         = self.game_mode,
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
            log.info("%s successfully synced to F1Laps" % self)
        else:
            log.info("%s failed sync to F1Laps" % self)
        return success, f1l_session_id
    
    def get_telemetry_string(self, lap):
        """ Get telemetry string of a specific lap for F1Laps sync """
        return json.dumps(lap.telemetry.frame_dict) if self.telemetry_enabled and lap.telemetry else None
    
    def get_f1laps_lap_times_list(self):
        lap_times = []
        for lap_number, lap_object in self.lap_list.items():
            if lap_object.sector_1_ms and lap_object.sector_2_ms and lap_object.sector_3_ms:
                lap_times.append({
                        "lap_number"           : lap_number,
                        "sector_1_time_ms"     : lap_object.sector_1_ms,
                        "sector_2_time_ms"     : lap_object.sector_2_ms,
                        "sector_3_time_ms"     : lap_object.sector_3_ms,
                        "car_race_position"    : lap_object.car_race_position,
                        "pit_status"           : lap_object.pit_status,
                        "tyre_compound_visual" : lap_object.tyre_compound_visual,
                        "telemetry_data_string": self.get_telemetry_string(lap_object)
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
                "grid_position": participant.grid_position or None,
                "lap_time_best": participant.lap_time_best or None,
                "race_time_total": participant.race_time_total or None,
                "penalties_time_total": participant.penalties_time_total or None,
                "penalties_number": participant.penalties_number or None
            })
        return classifications

    def has_final_classification(self):
        """ Check if session has been completed / has final classification """
        if bool(self.result_status):
            return True
        participants_count = len(self.participants)
        if not participants_count:
            return False
        last_participant = self.participants[participants_count-1]
        return bool(last_participant.result_status)
        
    