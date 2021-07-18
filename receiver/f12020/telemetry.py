from lib.logger import log
from receiver.telemetry_base import TelemetryBase, TelemetryLapBase, KEY_INDEX_MAP


class TelemetryLap(TelemetryLapBase):
    def clean_frame(self, frame_number):
        frame = self.frame_dict.get(frame_number)
        current_distance = None
        if not frame:
            return

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

        # Delete frames that are pre session FIRST LINE CROSS start
        if current_distance < 0:
            self.remove_frame(frame_number)
            return

        # If we have current and last lap distance, check that we're incrementing the distance
        if self.last_lap_distance:    
            
            # Check if last distance was higher - this means something UNEXPECTED happened
            if self.last_lap_distance > current_distance:

                # First, if current distance is SLIGHTLY less than last distance, we assume its a FLASHBACK
                # We pop any frame that has a greater distance
                if (self.last_lap_distance - current_distance) < self.MAX_FLASHBACK_DISTANCE_METERS:
                    log.info("Assuming a flashback happened - deleting all future frames")
                    for frame_key, frame_value in self.frame_dict.copy().items():
                        if frame_value[KEY_INDEX_MAP["lap_distance"]]\
                         and frame_value[KEY_INDEX_MAP["lap_distance"]] >= current_distance\
                         and frame_key != frame_number:
                            self.frame_dict.pop(frame_key)

                # There's another case: we came out of the garage, which doesnt increment the lap counter (weird!)
                # And lap distance pre line cross is NOT negative (also weird!)
                # So if we drop the current distance down to a super small number, we assume a NEW LAP was started
                elif current_distance < self.MAX_DISTANCE_COUNT_AS_NEW_LAP:
                    # New in F1 2021:
                    # Sometimes, the Lap Package gets sent after finish line cross (inlap) without incrementing the lapnumber
                    # In that case, the following code would remove the entire last lap. We dont want that. 
                    # So we add the condition that we only clean the pre-line frames if that pre-line frame_dict didn't contain
                    # frames that are early in the lap (meaning it wasnt a full lap)
                    frame_dict_sorted_by_distance = sorted(self.frame_dict.copy().items(), key=lambda kv: kv[KEY_INDEX_MAP["lap_distance"]])
                    first_frame_distance_frame, first_frame_distance_values = frame_dict_sorted_by_distance[0]
                    first_frame_distance_value = first_frame_distance_values[KEY_INDEX_MAP["lap_distance"]]
                    if first_frame_distance_value < self.MAX_DISTANCE_COUNT_AS_NEW_LAP:
                        log.info("Assuming an outlap started based on distance delta - killing all new frames (current distance %s, last distance %s, first frame distance %s)" % \
                            (current_distance, self.last_lap_distance, first_frame_distance_value))
                        self.remove_frame(frame_number)
                        # Important to return here to not set the last_lap_distance to the current_distance
                        return
                    else:
                        log.info("Assuming a new lap started based on distance delta - killing all old frames (current distance %s, last distance %s, first frame distance %s)" % \
                            (current_distance, self.last_lap_distance, first_frame_distance_value))
                        self.frame_dict = {frame_number: frame}
        
        # Set the last distance value for future frames
        self.last_lap_distance = current_distance


class Telemetry(TelemetryBase):
    TelemetryLapModel = TelemetryLap