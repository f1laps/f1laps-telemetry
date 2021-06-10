import ctypes

from receiver.game_version import CrossGamePacketHeader


class PacketHeader(CrossGamePacketHeader):
    pass


def unpack_udp_packet(packet):
    header = PacketHeader.from_buffer_copy(packet)
    
    # Map Header to Packet    
    packet_type = HeaderFieldsToPacketType[key]


    return packet_type.from_buffer_copy(packet)
