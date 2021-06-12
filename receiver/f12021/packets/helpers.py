from lib.logger import log
from .base import PacketHeader
from .session import PacketSessionData
from .lap import PacketLapData
from .participants import PacketParticipantsData
from .setup import PacketCarSetupData
from .telemetry import PacketCarTelemetryData
from .final_classification import PacketFinalClassificationData
from .session_history import PacketSessionHistoryData


HeaderFieldsToPacketType = {
     1: PacketSessionData,
     2: PacketLapData,
     4: PacketParticipantsData,
     5: PacketCarSetupData,
     6: PacketCarTelemetryData,
     8: PacketFinalClassificationData,
    11: PacketSessionHistoryData
}


def unpack_udp_packet(packet):
    """
    Important function - processes each packet
    First reads the header, which maps to the right body packet
    Returns the mapped body packet
    """
    header = PacketHeader.from_buffer_copy(packet)
    packet_type = HeaderFieldsToPacketType.get(header.packetId)
    log.info("Found packet type %s ID %s" % (packet_type, header.packetId))
    if packet_type:
        return packet_type.from_buffer_copy(packet)
    else:
        log.debug("Received unknown packet_type %s" % packet_type)
        return None
