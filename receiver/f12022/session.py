import logging
log = logging.getLogger(__name__)

from receiver.session_base import SessionBase, ParticipantBase
from .lap import F12022Lap
from .types import SessionType, Track
#from .api import F1LapsAPI2021
#from .telemetry import F12021Telemetry


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