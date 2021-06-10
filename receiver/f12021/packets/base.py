import ctypes

from receiver.game_version import CrossGamePacketHeader
from .session import PacketSessionData


HeaderFieldsToPacketType = {
    1: PacketSessionData,
    #2: Lap,
    #4: Participants,
    #5: Setup,
    #6: Telemetry,
    #8: Final Result,
    #11: Session History
}


class PacketBodyBase(ctypes.LittleEndianStructure):
    """
    Not sure if we need this, but good to have a customizable base class
    """
    pass


class PacketHeader(CrossGamePacketHeader):
    """ 
    The Packet Header is the same across F12020 and F12021
    Hence we use one shared HeaderClass for now
    May have to upgrade that logic if it changes
    """
    pass


def unpack_udp_packet(packet):
    """
    Important function - processes each packet
    First reads the header, which maps to the right body packet
    Returns the mapped body packet
    """
    header = PacketHeader.from_buffer_copy(packet)
    packet_type = HeaderFieldsToPacketType[header.packetId]
    return packet_type.from_buffer_copy(packet)
