from unittest import TestCase
from unittest.mock import MagicMock

from receiver.f12022.packets.session import PacketSessionData


class PacketSessionDataTest(TestCase):

    def test_serialize(self):
        packet = MockPacketSessionData()
        self.assertEqual(packet.serialize(),{
            'ai_difficulty': 99,
            'is_online_game': False,
            'is_spectating': 0,
            'packet_type': 'session',
            'session_type': 10,
            'session_uid': 123456,
            'track_id': 2,
            'weather_id': 2
        })
        


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


