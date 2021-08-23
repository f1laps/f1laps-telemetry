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
        if session.team_id is not None:
            # Don't update sessions with existing team_id
            return session
        from lib.logger import log
        log.info("************** MLOG PARTICIPANTS PACKET *************")
        log.info("Active cars: %s" % self.numActiveCars)
        for index, participant in enumerate(self.participants):
            log.info("[%s]: ai [%s] dId [%s] tId [%s] name[%s] yT [%s]" % (
                    index,
                    participant.aiControlled,
                    participant.driverId,
                    participant.teamId,
                    participant.name,
                    participant.yourTelemetry
                ))
        try:
            participant_data = self.participants[CAR_INDEX]
        except Exception as ex:
            log.info("Error retrieving team %s" % ex)
            return session
        udp_team_id = participant_data.teamId
        session.team_id = udp_team_id
        log.info("Set team to %s" % session.team_id)
        return session
