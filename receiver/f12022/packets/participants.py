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

    def serialize(self):
        try:
            participant_data = self.participants[self.header.playerCarIndex]
        except:
            return None
        participant_dict = {
            "packet_type": "participants",
            "team_id": participant_data.teamId,
            "num_participants": self.numActiveCars,
            "participants": []
        }
        # Add participant data array
        for index, participant in enumerate(self.participants):
            if (index+1) <= self.numActiveCars:
                participant_dict["participants"].append({
                    "driver": participant.driverId,
                    "driver_index": index,
                    "name": participant.name,
                    "team": participant.teamId,
                })
        return participant_dict
