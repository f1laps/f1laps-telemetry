from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12021.packets.lap import PacketLapData, LapData
from receiver.f12021.session import F12021Session


MOCK_LAP_NUMBER = 2


class PacketSessionHistoryDataTest(TestCase):

    def test_update_current_lap(self):
        session = F12021Session(123)
        packet = MockPacketLapData()
        session = packet.update_current_lap(session)
        self.assertEqual(session.lap_list, {MOCK_LAP_NUMBER: {'car_race_position': 10, 'is_valid': True, 'pit_status': 2}})
        packet.lapData[0].currentLapInvalid = 1
        packet.lapData[0].carPosition = 9
        packet.lapData[0].pitStatus = 0
        session = packet.update_current_lap(session)
        self.assertEqual(session.lap_list, {MOCK_LAP_NUMBER: {'car_race_position': 9, 'is_valid': False, 'pit_status': 2}})

    def test_update_telemetry(self):
        session = F12021Session(123)
        session.telemetry.start_new_lap(MOCK_LAP_NUMBER)
        packet = MockPacketLapData()
        session = packet.update_telemetry(session)
        self.assertEqual(session.telemetry.lap_dict[MOCK_LAP_NUMBER].frame_dict, {2345: [4321, 1543.0, None, None, None, None, None, None]})


if __name__ == '__main__':
    unittest.main()


class MockLapData(LapData):
    currentLapNum = MOCK_LAP_NUMBER
    carPosition = 10
    pitStatus = 2
    currentLapInvalid = 0
    currentLapTime = 1.543
    lapDistance = 4321


class MockPacketLapData(PacketLapData):
    header = MagicMock(playerCarIndex=0, frameIdentifier=2345)
    lapData = [MockLapData, ]

