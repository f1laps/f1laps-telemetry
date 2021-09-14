from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12021.packets.participants import PacketParticipantsData, ParticipantData
from receiver.f12021.session import F12021Session


class PacketParticipantsDataTest(TestCase):

    def test_update_team_id(self):
        packet = MockPacketParticipantsData()
        session = F12021Session(123)
        session = packet.process(session)
        self.assertEqual(session.team_id, 5)
        session = packet.process(session)
        self.assertEqual(session.team_id, 5)

    def test_update_participants(self):
        packet = MockPacketParticipantsData()
        session = F12021Session(123)
        session = packet.process(session)
        self.assertEqual(len(session.participants), 3)
        self.assertEqual(session.participants[0].team, 5)
        self.assertEqual(session.participants[1].driver_index, 1)
        self.assertEqual(session.participants[2].name, "Mick Schumi")
        # Test that data won't be duplicated
        session = packet.process(session)
        self.assertEqual(len(session.participants), 3)


if __name__ == '__main__':
    unittest.main()


class MockUserParticipantData(ParticipantData):
    teamId = 5
    driverId = 255
    name = "Player"

class MockAI1ParticipantData(ParticipantData):
    teamId = 3
    driverId = 1
    name = "Seb Vettel"

class MockAI2ParticipantData(ParticipantData):
    teamId = 2
    driverId = 2
    name = "Mick Schumi"


class MockPacketParticipantsData(PacketParticipantsData):
    header = MagicMock(playerCarIndex=0)
    numActiveCars = 3
    participants = [MockUserParticipantData, MockAI1ParticipantData, MockAI2ParticipantData]


