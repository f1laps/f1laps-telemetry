import ctypes

from .base import PacketBase, PacketHeader
from .base import CAR_INDEX


class ParticipantData(PacketBase):
    _fields_ = [
        ("aiControlled", ctypes.c_uint8),
        ("driverId", ctypes.c_uint8),
        ("networkId", ctypes.c_uint8),
        ("teamId", ctypes.c_uint8),
        ("myTeam", ctypes.c_uint8), # My team flag – 1 = My Team, 0 = otherwise
        ("raceNumber", ctypes.c_uint8),
        ("nationality", ctypes.c_uint8),
        ("name", ctypes.c_char * 48),
        ("yourTelemetry", ctypes.c_uint8), # The player's UDP setting, 0 = restricted, 1 = public
    ]


class PacketParticipantsData(PacketBase):
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

    def process(self, session):
        return self.update_team_id(session)

    def update_team_id(self, session):
        if session.team_id:
            # Don't update sessions with existing team_id
            return session
        from lib.logger import log
        log.info(repr(self))
        try:
            participant_data = self.participants[CAR_INDEX]
        except:
            return session
        udp_team_id = participant_data.teamId
        session.team_id = udp_team_id
        return session
