import json
import logging
log = logging.getLogger(__name__)

from receiver.lap_telemetry_base import LapTelemetryBase
from receiver.f12022.types import SESSION_TYPES_WITH_INLAP, \
                                  SESSION_TYPES_WITH_IN_AND_OUT_LAP, \
                                  SESSION_TYPES_TIME_TRIAL


class LapBase:
    """Holds all information about a lap""" 
    # Settings
    MAX_DISTANCE_COUNT_AS_NEW_LAP = 200

    def __init__(self, lap_number, session_type, telemetry_enabled):
        # Session info
        self.session_type = session_type

        # Lap info
        self.lap_number = lap_number
        self.sector_1_ms = None
        self.sector_2_ms = None
        self.sector_3_ms = None
        self.pit_status = None
        self.car_race_position = None
        self.is_valid = True
        self.tyre_compound_visual = None

        # Lap conditions
        self.air_temperature = None
        self.track_temperature = None
        self.rain_percentage_forecast = None
        self.weather_id = None

        # Tyre wear
        self.tyre_wear_current_values_temp_store = []
        self.lap_start_tyre_wear_front_left = None
        self.lap_start_tyre_wear_front_right = None
        self.lap_start_tyre_wear_rear_left = None
        self.lap_start_tyre_wear_rear_right = None
        self.sector_1_tyre_wear_front_left = None
        self.sector_1_tyre_wear_front_right = None
        self.sector_1_tyre_wear_rear_left = None
        self.sector_1_tyre_wear_rear_right = None
        self.sector_2_tyre_wear_front_left = None
        self.sector_2_tyre_wear_front_right = None
        self.sector_2_tyre_wear_rear_left = None
        self.sector_2_tyre_wear_rear_right = None
        self.sector_3_tyre_wear_front_left = None
        self.sector_3_tyre_wear_front_right = None
        self.sector_3_tyre_wear_rear_left = None
        self.sector_3_tyre_wear_rear_right = None

        # Telemetry
        self.telemetry = None
        self.telemetry_model = LapTelemetryBase

        # Penalties
        self.penalties = []

        # F1Laps sync
        self.has_been_synced_to_f1l = False
        self.telemetry_enabled = telemetry_enabled

        # Log lap init
        log.info("-----> %s started" % self)

    def __str__(self):
        return "Lap #%s" % self.lap_number
    
    def update(self, lap_values=None, telemetry_values=None):
        """Update the lap with new data"""
        # Get certain values that are needed later on 
        current_distance = telemetry_values.get("lap_distance")
        new_sector_1_time = lap_values.get("sector_1_ms")
        total_lap_time = telemetry_values.get("lap_time")
        new_pit_value = lap_values.get("pit_status")

        # Check in/out lap
        if self.is_in_or_outlap(current_distance, new_pit_value):
            # Don't update values for in or outlaps
            log.debug("%s is an inlap or outlap, not storing data" % self)
            
        elif lap_values and not self.new_lap_data_should_be_written(new_sector_1_time, total_lap_time):
            # Don't update values for laps that already have full data
            # This only applies to payloads with lap_data
            # Telemetry data should be written regardless
            log.debug("%s has all values set, not storing data" % self)
            self.reset_lap_telemetry()
            
        elif not lap_values and not self.telemetry:
            # Telemetry data gets sent in two packages
            # Lap packages -> has lap data and hence knows if telemetry data should be written
            # Telemetry package -> has no lap data and hence doesn't know if we can write it
            # So if we get telemetry data only, we only write if we had started to write already
            log.debug("%s has no telemetry data yet, not adding new telemetry data" % self)
            self.reset_lap_telemetry()
            
        else:
            # Init telemetry if we don't have it yet
            if not self.telemetry:
                self.init_telemetry()
            # Update this lap object
            for key, value in lap_values.items():
                setattr(self, key, value)
            # Update linked LapTelemetry object
            self.telemetry.update(telemetry_values)
            # Update tyre wear if we have it and if lap_values are set
            # It's important that we have lap_values so that we first determine if this is an 
            # in/outlap before writing the lap_start_tyre_wear
            if self.tyre_wear_current_values_temp_store and lap_values:
                log.info(">>>>>>>>> Pit value: %s" % new_pit_value)
                self.store_tyre_wear(*self.tyre_wear_current_values_temp_store)
        
    def init_telemetry(self):
        """ Init telemetry object """
        self.telemetry = self.telemetry_model(self.lap_number, self.session_type)
    
    def reset_lap_telemetry(self):
        """ 
        In time trial, we need to reset lap telemetry when using the "restart lap"
        It's not clear yet if this applies to other game modes too
        We're doing it for TT only for now
        """
        if self.session_type in SESSION_TYPES_TIME_TRIAL:
            # Reset telemetry
            self.telemetry = None
            log.debug("Reset telemetry for %s" % self)

    def new_lap_data_should_be_written(self, new_sector_1_time, total_lap_time):
        """
        Check if the current lap has all sector times, 
        in which case we don't overwrite it anymore
        """
        if self.session_type in SESSION_TYPES_TIME_TRIAL:
            return not self.is_restart_lap_time_trial(total_lap_time)
        all_sectors_set = bool(self.sector_1_ms and self.sector_2_ms and self.sector_3_ms)
        if all_sectors_set and new_sector_1_time in ["0", 0, None, ""]:
            return False
        return True
    
    def is_restart_lap_time_trial(self, total_lap_time):
        """
        In F1 22 Time Trial, when hitting "Restart Lap", the lap counter stays on the current lap,
        even though in-game it shows as lap-1 until finish line cross
        The lap distance remains positive.
        The current lap time stays 0 however, so we use that to check for restart laps
        """
        if not total_lap_time:
            return True
        return False
    
    def is_in_or_outlap(self, current_distance, new_pit_value):
        """Check if the current lap is an inlap or outlap"""
        if self.session_type in SESSION_TYPES_WITH_INLAP:
            return self.is_race_inlap(current_distance)
        # Quali sessions have inlaps and outlaps
        elif self.session_type in SESSION_TYPES_WITH_IN_AND_OUT_LAP:
            return self.is_quali_out_or_inlap(new_pit_value)
        else: # time trial, practice
            """ Todo: time trial outlaps """
            return False

    def is_race_inlap(self, current_distance):
        """ 
        Check if the current lap is an inlap in a race
        Reason: for race or OSQ inlaps (lap after last lap), the lap number doesn't increment
        Logic: If we're in the first x meters of a lap and also have all sector data -- it's an inlap
        """
        if (current_distance and current_distance < self.MAX_DISTANCE_COUNT_AS_NEW_LAP) and \
           self.sector_1_ms and self.sector_2_ms and self.sector_3_ms:
            log.debug("%s is a race inlap" % self)
            return True
        return False
    
    def is_quali_out_or_inlap(self, new_pit_value):
        """
        Check if the current lap is an in- or outlap in quali (where it's more complicated)
        Reason: for qualifying sessions (non-OSQ), the inlap and outlaps need to be ignored
        Logic: We check this based on pit status -- if no pits on entire lap, it's a real lap
        """
        return bool(new_pit_value is not None and new_pit_value > 0)
    
    def set_pit_status(self, pit_status):
        """
        Set the pit value for the current lap
        Pit status changes over the course of a lap
        We want to keep the highest number of:
            0 = no pit --- 1 = pit entry/exit --- 2 = pitting
        So that we store the "slowest" pit value
        """
        self.pit_status = max((self.pit_status or 0), (pit_status or 0))
        return self.pit_status
    
    def process_flashback_event(self, frame_id_flashed_back_to):
        """ Update telemetry frame dict after a flashback """
        # Update telemetry data
        if self.telemetry:
            self.telemetry.process_flashback_event(frame_id_flashed_back_to)
        # Remove any penalties that were flashed back
        # the [:] creates a copy of the list
        for penalty in self.penalties[:]:
            if penalty.frame_id > frame_id_flashed_back_to:
                self.penalties.remove(penalty)
    
    def can_be_synced_to_f1laps(self):
        """ Check if lap has all sectors and has not been synced to F1Laps before"""
        return bool(self.sector_1_ms and self.sector_2_ms and self.sector_3_ms) and not self.has_been_synced_to_f1l
    
    def recompute_sector_3_time(self, last_lap_time):
        """ After a lap is finished, we need to recompute S3 to make it accurate """
        if not last_lap_time or not self.sector_1_ms or not self.sector_2_ms:
            return None
        self.sector_3_ms = last_lap_time - self.sector_1_ms - self.sector_2_ms
    
    def json_serialize(self):
        """ Convert self to JSON """
        serialized_lap = {
            "lap_number": self.lap_number,
            "sector_1_time_ms": self.sector_1_ms,
            "sector_2_time_ms": self.sector_2_ms,
            "sector_3_time_ms": self.sector_3_ms,
            "pit_status": self.pit_status,
            "car_race_position": self.car_race_position,
            "tyre_compound_visual" : self.tyre_compound_visual,
            "telemetry_data_string": self.get_telemetry_string(),
            "penalties": [],
            "air_temperature": self.air_temperature,
            "track_temperature": self.track_temperature,
            "weather_id": self.weather_id,
            "rain_percentage_forecast": self.rain_percentage_forecast,
            "lap_start_tyre_wear_front_left": self.lap_start_tyre_wear_front_left,
            "lap_start_tyre_wear_front_right": self.lap_start_tyre_wear_front_right,
            "lap_start_tyre_wear_rear_left": self.lap_start_tyre_wear_rear_left,
            "lap_start_tyre_wear_rear_right": self.lap_start_tyre_wear_rear_right,
            "sector_1_tyre_wear_front_left": self.sector_1_tyre_wear_front_left,
            "sector_1_tyre_wear_front_right": self.sector_1_tyre_wear_front_right,
            "sector_1_tyre_wear_rear_left": self.sector_1_tyre_wear_rear_left,
            "sector_1_tyre_wear_rear_right": self.sector_1_tyre_wear_rear_right,
            "sector_2_tyre_wear_front_left": self.sector_2_tyre_wear_front_left,
            "sector_2_tyre_wear_front_right": self.sector_2_tyre_wear_front_right,
            "sector_2_tyre_wear_rear_left": self.sector_2_tyre_wear_rear_left,
            "sector_2_tyre_wear_rear_right": self.sector_2_tyre_wear_rear_right,
            "sector_3_tyre_wear_front_left": self.sector_3_tyre_wear_front_left,
            "sector_3_tyre_wear_front_right": self.sector_3_tyre_wear_front_right,
            "sector_3_tyre_wear_rear_left": self.sector_3_tyre_wear_rear_left,
            "sector_3_tyre_wear_rear_right": self.sector_3_tyre_wear_rear_right,
        }
        for penalty in self.penalties:
            serialized_lap["penalties"].append(penalty.json_serialize())
        return serialized_lap

    def get_telemetry_string(self):
        """ Get telemetry string of this lap for F1Laps sync """
        return json.dumps(self.telemetry.frame_dict) if self.telemetry and self.telemetry_enabled else None
    
    def get_current_sector_number(self):
        """ Return the current sector number as an integer """
        # The sector logic is:
        # When S1, all sectors have no time
        # When in S2, only S1 has its final time
        # When in S3, S1 and S2 have their finals times and S3 has live incrementing time
        if not self.sector_1_ms and not self.sector_2_ms and not self.sector_3_ms:
            return 1
        elif self.sector_1_ms and self.sector_2_ms and self.sector_3_ms:
            return 3
        else:
            return 2

    def store_tyre_wear(self, tyre_wear_front_left, tyre_wear_front_right, tyre_wear_rear_left, tyre_wear_rear_right):
        """ Store tyre wear data for this lap in the corresponding sector """
        # Don't store if any of the values is 0 or None:
        if not tyre_wear_front_left or not tyre_wear_front_right or not tyre_wear_rear_left or not tyre_wear_rear_right:
            return
        # Store at the end of the applicable sector 
        attribute_sector_key = "sector_{}".format(self.get_current_sector_number())
        setattr(self, "{}_tyre_wear_front_left".format(attribute_sector_key), tyre_wear_front_left)
        setattr(self, "{}_tyre_wear_front_right".format(attribute_sector_key), tyre_wear_front_right)
        setattr(self, "{}_tyre_wear_rear_left".format(attribute_sector_key), tyre_wear_rear_left)
        setattr(self, "{}_tyre_wear_rear_right".format(attribute_sector_key), tyre_wear_rear_right)
        # Store at the beginning of the lap - we just store it once and never overwrite it
        if not self.lap_start_tyre_wear_front_left:
            self.lap_start_tyre_wear_front_left = tyre_wear_front_left
            self.lap_start_tyre_wear_front_right = tyre_wear_front_right
            self.lap_start_tyre_wear_rear_left = tyre_wear_rear_left
            self.lap_start_tyre_wear_rear_right = tyre_wear_rear_right
            log.info('------------------ SETTTT')
        # Clear temp store
        self.tyre_wear_current_values_temp_store = []
