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
                 season_identifier=None,
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
        self.season_identifier = season_identifier

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

        # Overhead variables
        self.last_logged_distance = None # for minimap logging (motion packet)

        # Log session init
        log.info("*************************************************")
        log.info("New session started: %s" % self)
        log.info("*************************************************")
    
    def get_session_type(self):
        return SessionType.get(self.session_type)
    
    def get_track_name(self):
        return Track.get(self.track_id)
    
    def is_time_trial(self):
        """ Called by PenaltyBase """
        return not self.is_multi_lap_session()

    def update_weather(self, weather_id, track_temperature, air_temperature, rain_percentage_forecast):
        """ Given a new weather_id from the session packet, update the session's weather set """
        self.weather_ids.add(weather_id)
        # Update values in current lap
        current_lap = self.get_current_lap()
        if current_lap:
            current_lap.track_temperature = track_temperature
            current_lap.air_temperature = air_temperature
            current_lap.rain_percentage_forecast = rain_percentage_forecast
            current_lap.weather_id = weather_id

    
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
    
    def get_lap(self, lap_number, last_lap_time=None):
        """ 
        Return the Lap object for the given lap_number 
        If it doesn't exist, add it and return it
        Also sync lap - 1 (we need the last_lap_time to accurately calculate sector 3)
        """
        if lap_number not in self.lap_list:
            # Create new lap
            self.add_lap(lap_number)
            # Finish completed (previous) lap
            self.finish_completed_lap(lap_number - 1, last_lap_time)
        return self.lap_list[lap_number]
    
    def get_current_lap(self):
        """ Return the most recent (highest) Lap object in self.lap_list """
        return self.lap_list[max(self.lap_list)] if self.lap_list else None
    
    def add_lap(self, lap_number):
        """ Start a new lap by creating the Lap object and adding it to the lap_list """
        new_lap = F12022Lap(lap_number=lap_number, session_type=self.session_type, telemetry_enabled=self.telemetry_enabled)
        self.lap_list[lap_number] = new_lap
        return new_lap
    
    def finish_completed_lap(self, lap_number, last_lap_time):
        """ 
        Once a lap is completed, finish it 
        Use last_lap_time to re-compute the final sector 3 time
        """
        if lap_number not in self.lap_list:
            return
        # Update sector 3 time
        self.recompute_sector_3_lap_time(lap_number, last_lap_time)
        # Send to F1Laps
        return self.sync_to_f1laps(lap_number)
    
    def recompute_sector_3_lap_time(self, lap_number, final_lap_time):
        """ 
        Recompute the sector 3 lap time for the given lap_number 
        Called when:
        - a lap is finished, next lap started, and we update the last lap (via finish_completed_lap here)
        - in OSQ via the final classification packet processing
        """
        if not lap_number or not final_lap_time:
            return
        lap = self.lap_list.get(lap_number)
        if lap:
            lap.recompute_sector_3_time(final_lap_time)


    def is_valid_for_f1laps(self):
        """ Check if this session has all required data to be sent to F1Laps """
        if self.team_id is None:
            log.info("Session can't be synced to F1Laps because it has no team ID set")
            return False
        elif self.session_type is None:
            log.info("Session can't be synced to F1Laps because it has no session type set")
            return False
        return True 
    
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
        if not self.is_valid_for_f1laps() or (lap and not lap.can_be_synced_to_f1laps()):
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
        """ 
        Send individual lap to F1Laps 
        ! Gets called from sync_to_f1laps() and from PenaltyBase.send_to_f1laps()
        """
        if not lap:
            return False
        # Mark the lap as synced to F1Laps
        # Technically it depends on the API call, and we should mark it on success only
        # Unclear what the side effects are though 
        lap.has_been_synced_to_f1l = True
        # Send to API
        success = api.lap_create(
            track_id = self.track_id,
            team_id = self.team_id,
            conditions = self.map_weather_ids_to_f1laps_token(),
            # game_mode should always be time_trial
            # instead of hardcoding, we keep it dynamic to debug when needed
            game_mode = self.game_mode,
            sector_1_time = lap.sector_1_ms,
            sector_2_time = lap.sector_2_ms,
            sector_3_time = lap.sector_3_ms,
            setup_data = self.setup,
            is_valid = lap.is_valid,
            telemetry_data_string = lap.get_telemetry_string(),
            air_temperature = lap.air_temperature,
            track_temperature = lap.track_temperature,
            rain_percentage_forecast = lap.rain_percentage_forecast,
            weather_id = lap.weather_id,
            lap_start_tyre_wear_front_left = lap.lap_start_tyre_wear_front_left,
            lap_start_tyre_wear_front_right = lap.lap_start_tyre_wear_front_right,
            lap_start_tyre_wear_rear_left = lap.lap_start_tyre_wear_rear_left,
            lap_start_tyre_wear_rear_right = lap.lap_start_tyre_wear_rear_right,
            sector_1_tyre_wear_front_left = lap.sector_1_tyre_wear_front_left,
            sector_1_tyre_wear_front_right = lap.sector_1_tyre_wear_front_right,
            sector_1_tyre_wear_rear_left = lap.sector_1_tyre_wear_rear_left,
            sector_1_tyre_wear_rear_right = lap.sector_1_tyre_wear_rear_right,
            sector_2_tyre_wear_front_left = lap.sector_2_tyre_wear_front_left,
            sector_2_tyre_wear_front_right = lap.sector_2_tyre_wear_front_right,
            sector_2_tyre_wear_rear_left = lap.sector_2_tyre_wear_rear_left,
            sector_2_tyre_wear_rear_right = lap.sector_2_tyre_wear_rear_right,
            sector_3_tyre_wear_front_left = lap.sector_3_tyre_wear_front_left,
            sector_3_tyre_wear_front_right = lap.sector_3_tyre_wear_front_right,
            sector_3_tyre_wear_rear_left = lap.sector_3_tyre_wear_rear_left,
            sector_3_tyre_wear_rear_right = lap.sector_3_tyre_wear_rear_right,
            lap_start_ers_store_kj = lap.lap_start_ers_store_energy,
            sector_1_ers_store_kj = lap.sector_1_ers_store_energy,
            sector_2_ers_store_kj = lap.sector_2_ers_store_energy,
            sector_3_ers_store_kj = lap.sector_3_ers_store_energy,
            lap_start_fuel_remaining_kg = lap.lap_start_fuel_remaining,
            sector_1_fuel_remaining_kg = lap.sector_1_fuel_remaining,
            sector_2_fuel_remaining_kg = lap.sector_2_fuel_remaining,
            sector_3_fuel_remaining_kg = lap.sector_3_fuel_remaining,
            top_speed = lap.top_speed,
            number_gear_changes = lap.number_gear_changes,
            tyre_front_left_temp_max_surface = lap.tyre_front_left_temp_max_surface,
            tyre_front_right_temp_max_surface = lap.tyre_front_right_temp_max_surface,
            tyre_rear_left_temp_max_surface = lap.tyre_rear_left_temp_max_surface,
            tyre_rear_right_temp_max_surface = lap.tyre_rear_right_temp_max_surface,
            tyre_front_left_temp_max_inner = lap.tyre_front_left_temp_max_inner,
            tyre_front_right_temp_max_inner = lap.tyre_front_right_temp_max_inner,
            tyre_rear_left_temp_max_inner = lap.tyre_rear_left_temp_max_inner,
            tyre_rear_right_temp_max_inner = lap.tyre_rear_right_temp_max_inner,
        )
        if success:
            log.info("%s successfully synced to F1Laps" % lap)
        else:
            log.info("%s failed sync to F1Laps" % lap)
        return success
    
    def send_session_to_f1laps(self):
        """ Legacy method called by PenaltyBase """
        api = F1LapsAPI2022(self.f1laps_api_key, self.game_version)
        success, f1l_session_id = self.sync_session_to_f1laps(api)
        self.f1_laps_session_id = f1l_session_id
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
            classifications   = self.get_classification_list(),
            season_identifier = self.season_identifier
        )
        if success:
            log.info("%s successfully synced to F1Laps" % self)
        else:
            log.info("%s failed sync to F1Laps" % self)
        return success, f1l_session_id
    
    def get_f1laps_lap_times_list(self):
        lap_times = []
        for lap_number, lap_object in self.lap_list.items():
            if lap_object.sector_1_ms and lap_object.sector_2_ms and lap_object.sector_3_ms:
                lap_times.append(lap_object.json_serialize())
        return lap_times

    def get_classification_list(self):
        if not self.has_final_classification():
            return []
        classifications = []
        for participant in self.participants:
            # Only send participants that have a result_status
            if participant.result_status is None:
                continue
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
    
    def has_ended(self):
        """ Legacy method needed by PenaltyBase """
        return bool(self.finish_position is not None)
        
    