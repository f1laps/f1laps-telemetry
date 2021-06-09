import ctypes


class CrossGamePacketHeader(ctypes.LittleEndianStructure):
    _fields_ = [
            ("packetFormat", ctypes.c_uint16),
            ("gameMajorVersion", ctypes.c_uint8),
            ("gameMinorVersion", ctypes.c_uint8),
            ("packetVersion", ctypes.c_uint8),
            ("packetId", ctypes.c_uint8),
            ("sessionUID", ctypes.c_uint64),
            ("sessionTime", ctypes.c_float),
            ("frameIdentifier", ctypes.c_uint32),
            ("playerCarIndex", ctypes.c_uint8),
            ("secondaryPlayerCarIndex", ctypes.c_uint8),
        ]


UDP_PACKET_FORMAT_TO_GAME_VERSION_MAP = {
    2020: "f1_2020",
    2021: "f1_2021"
}


def parse_game_version_from_udp_packet(packet):
    """ 
    Input : UDP packet in bytes
    Output: Game Version as string
    """
    header = CrossGamePacketHeader.from_buffer_copy(packet)
    return UDP_PACKET_FORMAT_TO_GAME_VERSION_MAP[header.packetFormat]
    