import logging
log = logging.getLogger(__name__)

from receiver.f12022.packets.base import PacketHeader
#from receiver.f12022.packets.session import PacketSessionData
#from receiver.f12022.packets.lap import PacketLapData
#from receiver.f12022.packets.event import PacketEventData
#from receiver.f12022.packets.participants import PacketParticipantsData
#from receiver.f12022.packets.setup import PacketCarSetupData
#from receiver.f12022.packets.telemetry import PacketCarTelemetryData
#from receiver.f12022.packets.car_status import PacketCarStatusData
#from receiver.f12022.packets.final_classification import PacketFinalClassificationData
#from receiver.f12022.packets.session_history import PacketSessionHistoryData
#from receiver.f12022.packets.motion import PacketMotionData


HeaderFieldsToPacketType = {
     # The Motion packet sometimes returns:
     # 'Buffer size too small (36 instead of at least 1464 bytes)'
     # We don't need the packet in prod, only for maps, so we're skipping it by default.
     #0: PacketMotionData,
    #1: PacketSessionData,
    #2: PacketLapData,
    #3: PacketEventData,
    #4: PacketParticipantsData,
    #5: PacketCarSetupData,
    #6: PacketCarTelemetryData,
    #7: PacketCarStatusData,
    #8: PacketFinalClassificationData,
    #11: PacketSessionHistoryData
}


def unpack_udp_packet(packet):
    """
    Important function - processes each packet
    First reads the header, which maps to the right body packet
    Returns the mapped body packet
    """
    header = PacketHeader.from_buffer_copy(packet)
    packet_type = HeaderFieldsToPacketType.get(header.packetId)
    log.debug("Found packet type %s ID %s" % (packet_type, header.packetId))
    if packet_type:
        return packet_type.from_buffer_copy(packet)
    else:
        log.debug("Received unknown packet_type %s" % packet_type)
        return None
