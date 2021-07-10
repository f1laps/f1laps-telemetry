from lib.logger import log
from .packets.helpers import unpack_udp_packet

class F12021Processor:
    session = None
    f1laps_api_key = None
    telemetry_enabled = True

    def __init__(self, f1laps_api_key, enable_telemetry):
        self.f1laps_api_key = f1laps_api_key
        self.telemetry_enabled = enable_telemetry
        log.info("Started F1 2021 game processor")
        super(F12021Processor, self).__init__()

    def process(self, unpacked_packet):
        packet = unpack_udp_packet(unpacked_packet)
        if packet:
            # Process packet if we already have a session
            # or if packet sets a new session (i.e. the session packet)
            if self.session or packet.creates_session_object:
                self.session = packet.process(self.session)
                #log.info("PROCESSED %s and got %s" % (packet.__class__.__name__, self.session))
            if self.session:
                # Make sure session has user info
                self.session.f1laps_api_key = self.f1laps_api_key
                self.session.telemetry_enabled = self.telemetry_enabled