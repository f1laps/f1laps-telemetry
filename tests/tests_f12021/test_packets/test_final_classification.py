from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12021.packets.final_classification import FinalClassificationData, PacketFinalClassificationData
from receiver.f12021.session import F12021Session

class PacketFinalClassificationDataTest(TestCase):

    @patch('receiver.f12021.session.F12021Session.send_session_to_f1laps')
    def test_process(self, mock_send_to_f1laps):
        session = F12021Session(123)
        packet = MockPacketFinalClassificationData()
        packet.process(session)
        self.assertEqual(session.finish_position, 5)
        self.assertEqual(session.result_status, 6)
        self.assertEqual(session.points, 8)
        mock_send_to_f1laps.assert_called_with()


if __name__ == '__main__':
    unittest.main()


class MockFinalClassificationData(FinalClassificationData):
    position = 5
    resultStatus = 6
    points = 8


class MockPacketFinalClassificationData(PacketFinalClassificationData):
    header = MagicMock(playerCarIndex=0)
    carIdx = 0
    classificationData = [MockFinalClassificationData, ]

