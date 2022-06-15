import json
import logging
log = logging.getLogger(__name__)

from receiver.session_base import SessionBase, ParticipantBase
from receiver.f12022.lap import F12022Lap
from receiver.f12022.types import SessionType, Track
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
                 team_id=None,
                ):
        # Meta
        self.f1laps_api_key = f1laps_api_key
        self.telemetry_enabled = telemetry_enabled
        self.game_version = "f12022"
        
        # Session
        self.session_udp_uid = session_uid
        self.session_type = session_type
        self.session_type_name = SessionType.get(session_type)
        self.track_id = track_id
        self.track_name = Track.get(track_id)
        self.team_id = team_id
        self.is_online_game = is_online_game
        self.ai_difficulty = ai_difficulty
        self.weather_ids = set([weather_id]) # set() maintains uniqueness

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
        log.info("New session started: %s %s (ID %s)" % (self.track_name, self.session_type_name, self.session_udp_uid))
        log.info("*************************************************")

    def update_weather(self, weather_id):
        """ Given a new weather_id from the session packet, update the session's weather set """
        self.weather_ids.add(weather_id)
    
    def get_lap(self, lap_number):
        """ 
        Return the Lap object for the given lap_number 
        If it doesn't exist, add it and return it
        """
        if lap_number not in self.lap_list:
            # Create new lap
            self.add_lap(lap_number)
            # Finish completed (previous) lap
            self.finish_completed_lap(lap_number - 1)
        return self.lap_list[lap_number]
    
    def add_lap(self, lap_number):
        """ Start a new lap by creating the Lap object and adding it to the lap_list """
        new_lap = F12022Lap(lap_number)
        self.lap_list[lap_number] = new_lap
        return new_lap
    
    def finish_completed_lap(self, lap_number):
        """ Once a lap is completed, finish it """
        pass

    def can_be_synced_to_f1laps(self):
        """ Check if this session has all required data to be sent to F1Laps """
        return self.team_id and self.session_type
    
    def is_multi_lap_session(self):
        """ Check if this session gets synced as session or individual laps """

    def sync_to_f1laps(self, lap_number):
        """ Send a lap or session to F1Laps, if it's ready for sync """
        lap = self.get_lap(lap_number)
        if not self.can_be_synced_to_f1laps or not lap.can_be_synced_to_f1laps():
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
            game_mode             = self.session_type_name,
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
    
    def sync_session_to_f1laps(self, lap, api):
        """ Send full sessiom to F1Laps """
        success, f1l_session_id = api.session_create_or_update(
            f1laps_session_id = self.f1_laps_session_id,
            track_id          = self.track_id,
            team_id           = self.team_id,
            session_uid       = self.session_udp_uid,
            conditions        = self.map_weather_ids_to_f1laps_token(),
            session_type      = self.session_type_name,
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
        return json.dumps(lap.telemetry.frame_dict) if self.telemetry_enabled else None
    
    def get_f1laps_lap_times_list(self):
        lap_times = []
        for lap_number, lap_object in self.lap_list.items():
            if lap_object.self.sector_1_ms and lap_object.sector_2_ms and lap_object.sector_3_ms:
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
        
    