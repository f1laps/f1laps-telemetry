from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12021.packets.participants import PacketParticipantsData, ParticipantData
from receiver.f12021.session import F12021Session


class PacketParticipantsDataTest(TestCase):

    def test_process(self):
        packet = MockPacketParticipantsData()
        session = F12021Session(123)
        session.team_id = None
        session = packet.process(session)
        self.assertEqual(session.team_id, 5)
        session = packet.process(session)
        self.assertEqual(session.team_id, 5)
    


if __name__ == '__main__':
    unittest.main()


class MockParticipantData(ParticipantData):
    teamId = 5


class MockPacketParticipantsData(PacketParticipantsData):
    header = MagicMock(playerCarIndex=0)
    participants = [MockParticipantData, ]


