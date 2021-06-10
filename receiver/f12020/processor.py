import f1_2020_telemetry.packets
from lib.logger import log

from receiver.f12020.packets import SessionPacket, ParticipantsPacket, CarSetupPacket, \
                             FinalClassificationPacket, LapPacket, CarStatusPacket, \
                             TelemetryPacket

class F12020Processor:
    session = None
    f1laps_api_key = None
    telemetry_enabled = True

    def __init__(self, f1laps_api_key, enable_telemetry):
        self.f1laps_api_key = f1laps_api_key
        self.telemetry_enabled = enable_telemetry
        log.info("Instantiated F1 2020 game processor")
        super(F12020Processor, self).__init__()

    def process(unpacked_packet):
        packet = f1_2020_telemetry.packets.unpack_udp_packet(unpacked_packet)

        # process session packets first
        # the session packet class returns a session object 
        # it doesn't change the session for existing sessions
        # it returns a new session object for new sessions
        if isinstance(packet, f1_2020_telemetry.packets.PacketSessionData_V1):
            self.session = SessionPacket().process(packet, self.session)
            if self.session:
                self.session.f1laps_api_key = self.f1laps_api_key
                self.session.telemetry_enabled = self.telemetry_enabled

        # dont do anything else if there isnt a session set
        if self.session:

            # Now we listen to the actual race information
            # Each package gets processed in real-time as it comes in

            # Participants
            if isinstance(packet, f1_2020_telemetry.packets.PacketParticipantsData_V1):
                ParticipantsPacket().process(packet, self.session)

            # Setup
            if isinstance(packet, f1_2020_telemetry.packets.PacketCarSetupData_V1):
                CarSetupPacket().process(packet, self.session)

            # Lap Data
            if isinstance(packet, f1_2020_telemetry.packets.PacketLapData_V1):
                LapPacket().process(packet, self.session)

            # Car Status Data
            if isinstance(packet, f1_2020_telemetry.packets.PacketCarStatusData_V1):
                CarStatusPacket().process(packet, self.session)

            # Telemetry Data
            if isinstance(packet, f1_2020_telemetry.packets.PacketCarTelemetryData_V1):
                TelemetryPacket().process(packet, self.session)

            # Final Classification
            if isinstance(packet, f1_2020_telemetry.packets.PacketFinalClassificationData_V1):
                FinalClassificationPacket().process(packet, self.session)