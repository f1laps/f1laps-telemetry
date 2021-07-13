from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12021.packets.session import PacketSessionData
from receiver.f12021.session import F12021Session


class PacketSessionDataTest(TestCase):

    def test_is_active_session(self):
        packet = MockPacketSessionData()
        self.assertEqual(packet.is_active_session(None), False)
        session = F12021Session(123)
        self.assertEqual(packet.is_active_session(session), False)
        session = F12021Session(MockPacketSessionData.header.sessionUID)
        self.assertEqual(packet.is_active_session(session), True)

    def test_process_spectating(self):
        packet = MockPacketSessionData()
        packet.isSpectating = 1
        self.assertEqual(packet.process(None), None)

    def test_process_active(self):
        packet = MockPacketSessionData()
        session = F12021Session(MockPacketSessionData.header.sessionUID)
        self.assertEqual(packet.process(session), session)

    def test_process_new(self):
        packet = MockPacketSessionData()
        session = packet.process(None)
        self.assertEqual(session.session_udp_uid, 123456)
        self.assertEqual(session.session_type, 10)
        self.assertEqual(session.track_id, 2)
        self.assertEqual(session.ai_difficulty, 99)
        self.assertEqual(session.is_online_game, False)
        self.assertEqual(session.weather_ids, [2])


if __name__ == '__main__':
    unittest.main()



class MockPacketSessionData(PacketSessionData):
    header = MagicMock(playerCarIndex=0, sessionUID=123456)
    isSpectating = 0
    sessionType = 10
    trackId = 2
    aiDifficulty = 99
    networkGame = 0
    weather = 2
    seasonLinkIdentifier = 1
    weekendLinkIdentifier = 2
    sessionLinkIdentifier = 3


