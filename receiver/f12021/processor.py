from lib.logger import log
from .packets.base import unpack_udp_packet

class F12021Processor:
    session = None
    f1laps_api_key = None
    telemetry_enabled = True

    def __init__(self, f1laps_api_key, enable_telemetry):
        self.f1laps_api_key = f1laps_api_key
        self.telemetry_enabled = enable_telemetry
        log.info("Started F1 2021 game processor")
        super(F12021Processor, self).__init__()

    def process(unpacked_packet):
        packet = unpack_udp_packet(unpacked_packet)
        log.info("---------------------------------------------------")
        log.info("Received packet with ID %s" % packet.header.packetId)
        log.info(repr(packet))
        