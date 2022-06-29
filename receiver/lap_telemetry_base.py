import logging
log = logging.getLogger(__name__)


KEY_INDEX_MAP = {
    "lap_distance": 0,
    "lap_time"    : 1,
    "speed"       : 2,
    "brake"       : 3,
    "throttle"    : 4,
    "gear"        : 5,
    "steer"       : 6,
    "drs"         : 7,
}

KEY_ROUND_MAP = {
    "lap_distance": 2,
    "lap_time"    : 0,
    "speed"       : 0,
    "brake"       : 3,
    "throttle"    : 3,
    "gear"        : 0,
    "steer"       : 3,
    "drs"         : 0,
}


class LapTelemetryBase:
    """Holds current lap telemetry data"""
    MAX_FLASHBACK_DISTANCE_METERS = 1500
    MAX_DISTANCE_COUNT_AS_NEW_LAP = 200

    def __init__(self, lap_number, session_type=None):
        # Lap number
        self.lap_number = lap_number

        # Session types matter:
        # Time trial lets you restart a lap
        # Other game modes have outlaps (TT doesnt)
        # This distinction is important because for outlaps, we dont want the outlap frames
        # But for restart, we want the new lap frames
        self.session_type = session_type
        SESSION_TYPES_WITHOUT_OUTLAP = [1, 2, 3, 4, 13]

        # Main frame dict
        # Each frame is a key in this dict
        # Each holds a list of the telemetry values
        self.frame_dict = {}

        # Last lap distance
        # Ensure we're incrementing lap distance
        # If we don't, we need to remove the dict
        self.last_lap_distance = None

        # Popped frames list
        # Store which frames got popped 
        self.frames_popped_list = []
    
    def update(self, telemetry_dict):
        """ Update this LapTelemetry object's frame dict"""
        # Pop frame_id out of the dict because we'll set all attributes later and cant set the id
        frame_number = telemetry_dict.pop("frame_identifier")
        frame = self.get_frame(frame_number)
        for key, value in telemetry_dict.items():
            frame_index    = KEY_INDEX_MAP[key]
            decimal_points = KEY_ROUND_MAP[key]
            frame[frame_index] = round(value, decimal_points)
        self.clean_frame(frame_number)
    
    def get_frame(self, frame_number):
        """ 
        Helper function that returns a given frame from frame_dict or creates it
        If frame doesn't exist in frame dict yet, create it with empty values 
        """
        if frame_number not in self.frame_dict:
            self.frame_dict[frame_number] = []
            for _ in range(0, len(KEY_INDEX_MAP)):
                self.frame_dict[frame_number].append(None)
        return self.frame_dict[frame_number]

    def clean_frame(self, frame_number):
        """ 
        Clean up frame dict with various annoyances that the F1 game telemetry has
        """
        frame = self.frame_dict.get(frame_number)
        current_distance = None

        # Check if we popped this frame before - if so, don't populate it again
        if frame_number in self.frames_popped_list:
            self.frame_dict.pop(frame_number)
            return 

        # Get lap distance of current frame
        current_distance = frame[KEY_INDEX_MAP["lap_distance"]]

        # The telemetry packet doesn't set lap distance, so we may not have distance yet - return if so
        if not current_distance:
            return

        # This should never happen, but let's make sure that distance is a number
        if not isinstance(current_distance, float) and not isinstance(current_distance, int):
            return

        # Reset telemetry when we are pre session FIRST LINE CROSS start
        if current_distance < 0:
            log.debug("Resetting telemetry because we are pre session first line cross")
            self.frame_dict = {}
            # In F1 2021, in an outlap in TT, the first frame sends a positive value (e.g. distance of 126)
            # Then switches to negative values as expected in an outlap
            # So we need to manually reset the last lap distance to None here
            self.last_lap_distance = None
            return
        
        # Set the last distance value for future frames
        self.last_lap_distance = current_distance

    def remove_frame(self, frame_number):
        self.frame_dict.pop(frame_number)
        self.frames_popped_list.append(frame_number)

    def process_flashback_event(self, frame_id_flashed_back_to):
        current_frame_max = max(self.frame_dict) if self.frame_dict else None
        deleted_frame_count = 0

        # Delete frames until we get to the frame we flashed back to
        for frame_id, _ in self.frame_dict.copy().items():
            if frame_id >= frame_id_flashed_back_to:
                deleted_frame_count += 1
                self.frame_dict.pop(frame_id)
        
        # Reset last lap distance
        self.last_lap_distance = None
        log.debug("Removed frames that were flashbacked away (flbk to %s; max was %s; deleted %s)" % (
            frame_id_flashed_back_to,
            current_frame_max,
            deleted_frame_count
            ))