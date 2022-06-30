import logging
log = logging.getLogger(__name__)

from receiver.f12022.packets.helpers import unpack_udp_packet
from receiver.f12022.session import F12022Session
from receiver.f12022.penalty import F12022Penalty
from receiver.f12022.types import SESSION_TYPE_OSQ


class F12022Processor:
    session = None
    f1laps_api_key = None
    telemetry_enabled = True

    def __init__(self, f1laps_api_key, enable_telemetry):
        self.f1laps_api_key = f1laps_api_key
        self.telemetry_enabled = enable_telemetry
        log.info("Started F1 2022 game processor")
        super(F12022Processor, self).__init__()

    def process(self, unpacked_packet):
        try:
            packet = unpack_udp_packet(unpacked_packet)
        except Exception as ex:
            log.info("Couldn't unpack packet due to %s" % ex)
            packet = None

        if packet:
            # If we don't have a session yet, we only process the 
            # Session packet (identified via packet.creates_session_object)
            if not self.session:
                if packet.creates_session_object:
                    session_data = packet.serialize()
                    # Create a new session if the user is not spectating
                    if not session_data['is_spectating']:
                        self.session = self.create_session(session_data)
            # If we already have a session, process packet data
            if self.session:
                packet_data = packet.serialize()
                if packet_data:
                    self.process_serialized_packet(packet_data)
            
    def process_serialized_packet(self, packet_data):
        """ Given a serialized packet, process it """
        if not packet_data.get("packet_type"):
            return False
        elif packet_data["packet_type"] == "session":
            self.process_session_packet(packet_data)
        elif packet_data["packet_type"] == "lap":
            self.process_lap_packet(packet_data)
        elif packet_data["packet_type"] == "telemetry":
            self.process_telemetry_packet(packet_data)
        elif packet_data["packet_type"] == "participants":
            self.process_participant_data(packet_data)
        elif packet_data["packet_type"] == "setup":
            self.process_setup_packet(packet_data)
        elif packet_data["packet_type"] == "final_classification":
            self.process_final_classifictation_packet(packet_data)
        elif packet_data["packet_type"] == "event":
            self.process_event_packet(packet_data)
        elif packet_data["packet_type"] == "car_status":
            self.process_car_status_packet(packet_data)
        return True
    
    def process_session_packet(self, packet_data):
        """ 
        Start new session if UDP ID changes
        Update weather info for running sessions
        """
        if packet_data["session_uid"] != self.session.session_udp_uid:
            # Update session if UDP changed
            log.info("Session UDP has changed from %s to %s. Creating new session." \
                % (self.session.session_udp_uid, packet_data["session_uid"]))
            self.session = self.create_session(packet_data)
        else:
            # Update session weather 
            self.session.update_weather(packet_data["weather_id"])
            # Add session type if it's not set
            # This should never happen but we have seen sessions without session type
            # So let's just make sure
            if not self.session.session_type and packet_data["session_type"] is not None:
                self.session.session_type = packet_data["session_type"]
        
    def create_session(self, packet_data):
        return F12022Session(self.f1laps_api_key, 
                             self.telemetry_enabled, 
                             packet_data["session_uid"],
                             packet_data["session_type"],
                             packet_data["track_id"],
                             packet_data["is_online_game"],
                             packet_data["ai_difficulty"],
                             packet_data["weather_id"],
                             packet_data["game_mode"]
                            )
    
    def process_lap_packet(self, packet_data):
        lap_number = packet_data.get("lap_number")
        if not lap_number:
            # If we can't retrieve lap number, we can't do anything
            return 
        # Get lap object 
        last_lap_time = packet_data.get("last_laptime_ms")
        lap = self.session.get_lap(lap_number, last_lap_time)
        # Update lap
        lap.update(
            lap_values = {
                "sector_1_ms": packet_data.get("sector_1_ms"),
                "sector_2_ms": packet_data.get("sector_2_ms"),
                "sector_3_ms": packet_data.get("sector_3_ms"),
                "pit_status": packet_data.get("pit_status"),
                "is_valid": packet_data.get("is_valid"),
                "car_race_position": packet_data.get("car_race_position")
            },
            telemetry_values = {
                "lap_distance": packet_data.get("lap_distance"),
                "frame_identifier": packet_data.get("frame_identifier"),
                "lap_time": packet_data.get("current_laptime_ms"),
            }
        )
    
    def process_telemetry_packet(self, packet_data):
        # Get lap object 
        lap = self.session.get_current_lap()
        lap.update(
            lap_values = {},
            telemetry_values = {
                "frame_identifier": packet_data.get("frame_identifier"),
                "speed": packet_data.get("speed"),
                "brake": packet_data.get("brake"),
                "throttle": packet_data.get("throttle"),
                "gear": packet_data.get("gear"),
                "steer": packet_data.get("steer"),
                "drs": packet_data.get("drs"),
            }
        )
    
    def process_participant_data(self, packet_data):
        """
        Add team ID to session if it isn't set yet
        Add participants to session if not all are set yet
        """
        # Add user's team ID to session
        # Team_ids need to be tested against None (not 0, which is a valid value)
        if packet_data.get("team_id") is not None and self.session.team_id is None:
            self.session.set_team_id(packet_data["team_id"])
        # Add all participants to session (if not already added)
        if packet_data.get("participants") and \
            len(self.session.participants) < packet_data.get("num_participants"):
            for participant in packet_data.get("participants"):
                self.session.add_participant(participant)
    
    def process_setup_packet(self, packet_data):
        """
        Add setup to session
        Update it continuously in case the user made changes
        """
        self.session.setup = {
            "front_wing": packet_data.get("front_wing"),
            "rear_wing": packet_data.get("rear_wing"),
            "diff_adjustment_on_throttle": packet_data.get("diff_adjustment_on_throttle"),
            "diff_adjustment_off_throttle": packet_data.get("diff_adjustment_off_throttle"),
            "front_camber": packet_data.get("front_camber"),
            "rear_camber": packet_data.get("rear_camber"),
            "front_toe": packet_data.get("front_toe"),
            "rear_toe": packet_data.get("rear_toe"),
            "front_suspension": packet_data.get("front_suspension"),
            "rear_suspension": packet_data.get("rear_suspension"),
            "front_antiroll_bar": packet_data.get("front_antiroll_bar"),
            "rear_antiroll_bar": packet_data.get("rear_antiroll_bar"),
            "front_ride_height": packet_data.get("front_ride_height"),
            "rear_ride_height": packet_data.get("rear_ride_height"),
            "brake_pressure": packet_data.get("brake_pressure"),
            "front_brake_bias": packet_data.get("front_brake_bias"),
            "front_right_tyre_pressure": packet_data.get("front_right_tyre_pressure"),
            "front_left_tyre_pressure": packet_data.get("front_left_tyre_pressure"),
            "rear_right_tyre_pressure": packet_data.get("rear_right_tyre_pressure"),
            "rear_left_tyre_pressure": packet_data.get("rear_left_tyre_pressure"),
        }
    
    def process_final_classifictation_packet(self, packet_data):
        # Set session final classification data
        self.session.finish_position = packet_data.get("finish_position")
        self.session.result_status   = packet_data.get("result_status")
        self.session.points          = packet_data.get("points")
        # Set each participant's final classification data
        for index, classification in packet_data.get("all_participants_results").items():
            try:
                participant = self.session.participants[int(index)]
            except:
                continue
            participant.points = classification.get("points")
            participant.finish_position = classification.get("finish_position")
            participant.grid_position = classification.get("grid_position")
            participant.result_status = classification.get("result_status")
            participant.lap_time_best = classification.get("lap_time_best")
            participant.penalties_number = classification.get("penalties_number")
            participant.race_time_total = classification.get("race_time_total")
            participant.penalties_time_total = classification.get("penalties_time_total")
        # For OSQ, update the best lap time
        # Needed because OSQ don't send the lastLapTimeMS in the lap packet
        # So we need this for an accurate sector 3 time
        best_lap_time = packet_data.get("user_lap_time_best")
        if self.session.session_type == SESSION_TYPE_OSQ and best_lap_time:
            osq_lap_number = 1
            self.session.recompute_sector_3_lap_time(osq_lap_number, best_lap_time)
        # Sync to F1L
        self.session.sync_to_f1laps(lap_number=None, sync_entire_session=True)
    
    def process_event_packet(self, packet_data):
        """ Process various types of ad-hoc game events """
        if not packet_data.get("event_type"):
            return
        elif packet_data.get("event_type") == "flashback":
            self.process_flashback_event_packet(packet_data)
        elif packet_data.get("event_type") == "penalty":
            self.process_penalty_event_packet(packet_data)
    
    def process_flashback_event_packet(self, packet_data):
        """ Call current lap's process_flashback_event_packet method """
        frame_id = packet_data.get("frame_identifier")
        session_time = packet_data.get("session_time")
        log.info("Event: Flashback happened to frame %s and session time %s. Deleting frames." % (frame_id, session_time))
        self.session.get_current_lap().process_flashback_event(frame_id)
    
    def process_penalty_event_packet(self, packet_data):
        """ Create Penalty object and send it to F1Laps """
        penalty = F12022Penalty()
        penalty.penalty_type = packet_data.get("penalty_type")
        penalty.infringement_type = packet_data.get("infringement_type")
        penalty.vehicle_index = packet_data.get("vehicle_index")
        penalty.other_vehicle_index = packet_data.get("other_vehicle_index")
        penalty.time_spent_gained = packet_data.get("time_spent_gained")
        penalty.lap_number = packet_data.get("lap_number")
        penalty.places_gained = packet_data.get("places_gained")
        penalty.session = self.session
        log.info("Processing %s" % penalty)
        penalty.send_to_f1laps()
    
    def process_car_status_packet(self, packet_data):
        """ Update tyres used for the current lap """
        current_lap = self.session.get_current_lap()
        current_lap.tyre_compound_visual = packet_data.get("tyre_compound_visual")