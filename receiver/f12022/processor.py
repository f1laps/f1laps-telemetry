import logging
log = logging.getLogger(__name__)

from receiver.f12022.packets.helpers import unpack_udp_packet
from receiver.f12022.session import F12022Session


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
        packet = unpack_udp_packet(unpacked_packet)
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
                if not packet.get("packet_type"):
                    pass
                elif packet_data["packet_type"] == "session":
                    self.process_session_packet(packet_data)
                elif packet_data["packet_type"] == "lap":
                    self.process_lap_packet(packet_data)
                elif packet_data["packet_type"] == "event":
                    pass
                elif packet_data["packet_type"] == "participant":
                    pass
                elif packet_data["packet_type"] == "setup":
                    pass
                elif packet_data["packet_type"] == "telemetry":
                    pass
                elif packet_data["packet_type"] == "car_status":
                    pass
                elif packet_data["packet_type"] == "classification":
                    pass
    
    def process_session_packet(self, packet_data):
        if packet_data["session_uid"] != self.session.session_udp_uid:
            # Update session if UDP changed
            log.info("Session UDP has changed from %s to %s. Creating new session." \
                % (self.session.session_udp_uid, packet_data["session_uid"]))
            self.session = self.create_session(packet_data)
        else:
            # Update session weather 
            self.session.update_weather(packet_data["weather_id"])
    
    def process_lap_packet(self, packet_data):
        lap_number = packet_data.get("lap_number")
        if not lap_number:
            # If we can't retrieve lap number, we can't do anything
            return 
        # Get lap object 
        lap = self.session.get_lap(lap_number)
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
    
    def create_session(self, session_data):
        return F12022Session(self.f1laps_api_key, 
                             self.telemetry_enabled, 
                             session_data["session_uid"],
                             session_data["session_type"],
                             session_data["track_id"],
                             session_data["is_online_game"],
                             session_data["ai_difficulty"],
                             session_data["weather_id"]
                            )