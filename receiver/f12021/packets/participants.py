import ctypes

from .base import PacketBase, PacketHeader


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
        self.update_team_id(session)
        self.update_participants(session)
        return session

    def update_team_id(self, session):
        if session.team_id:
            # Don't update sessions with existing team_id
            return 
        try:
            participant_data = self.participants[self.header.playerCarIndex]
        except:
            return 
        udp_team_id = participant_data.teamId
        session.team_id = udp_team_id

    def update_participants(self, session):
        if len(session.participants) >= self.numActiveCars:
            # Don't update participants when they're already set
            return 
        for index, participant in enumerate(self.participants):
            session.add_participant(
                name = participant.name,
                team = participant.teamId,
                driver = participant.driverId,
                driver_index = index
            )
