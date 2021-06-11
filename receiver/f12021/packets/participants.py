from .base import PacketBodyBase, PacketHeader


class ParticipantData(PacketBodyBase):
    _fields_ = [
        ("aiControlled", ctypes.c_uint8),
        ("driverId", ctypes.c_uint8),
        ("teamId", ctypes.c_uint8),
        ("myTeam", ctypes.c_uint8), # My team flag – 1 = My Team, 0 = otherwise
        ("raceNumber", ctypes.c_uint8),
        ("nationality", ctypes.c_uint8),
        ("name", ctypes.c_char * 48),
        ("yourTelemetry", ctypes.c_uint8), # The player's UDP setting, 0 = restricted, 1 = public
    ]


class PacketParticipantsData(PacketBodyBase):
    """
    This is a list of participants in the race.
    Frequency: Every 5 seconds
    Size: 1257 bytes
    Version: 1
    """
    _fields_ = [
        ("header", PacketHeader),
        ("numActiveCars", ctypes.c_uint8),
        ("participants", ParticipantData * 22),
    ]
