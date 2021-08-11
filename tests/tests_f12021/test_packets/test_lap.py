from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12021.packets.lap import PacketLapData, LapData
from receiver.f12021.session import F12021Session


MOCK_LAP_NUMBER = 2


class PacketLapDataTest(TestCase):

    def test_process_current_lap(self):
        session = F12021Session(123)
        session.complete_lap_v2 = MagicMock()
        # Start new lap 2 so that we only test update, not create
        session.start_new_lap(MOCK_LAP_NUMBER)
        session.lap_list = {MOCK_LAP_NUMBER: {'car_race_position': 5, 'is_valid': True, 'pit_status': 1}}
        packet = MockPacketLapData()
        session = packet.process(session)
        self.assertEqual(session.lap_list, 
                         {MOCK_LAP_NUMBER: {'car_race_position': 10, 'is_valid': True, 'lap_number': 2, 'pit_status': 2, 'sector_1_ms': 1000, 'sector_2_ms': 543, 'sector_3_ms': None}})
        self.assertEqual(session.telemetry.lap_dict[MOCK_LAP_NUMBER].frame_dict, {2345: [4321, 1543.0, None, None, None, None, None, None]})
        self.assertEqual(session.complete_lap_v2.call_count, 0)

    def test_process_new_lap(self):
        session = F12021Session(123)
        session.complete_lap_v2 = MagicMock()
        packet = MockPacketLapData()
        session = packet.process(session)
        self.assertEqual(session.lap_list, 
                         {MOCK_LAP_NUMBER: {'car_race_position': 10, 'is_valid': True, 'lap_number': 2, 'pit_status': 2, 'sector_1_ms': 1000, 'sector_2_ms': 543, 'sector_3_ms': None}})
        self.assertEqual(session.telemetry.lap_dict[MOCK_LAP_NUMBER].frame_dict, {2345: [4321, 1543.0, None, None, None, None, None, None]})
        self.assertEqual(session.complete_lap_v2.call_count, 1)

    def test_process_new_lap_with_previous(self):
        session = F12021Session(123)
        session.complete_lap_v2 = MagicMock()
        # Start new lap 1 so that we test updating previous
        prev_lap_num = MOCK_LAP_NUMBER - 1
        session.start_new_lap(prev_lap_num)
        session.lap_list[prev_lap_num] = {'sector_1_ms': 500, 'sector_2_ms': 400}
        packet = MockPacketLapData()
        session = packet.process(session)
        self.assertEqual(session.lap_list, 
                         {prev_lap_num: {'sector_1_ms': 500, 'sector_2_ms': 400, 'sector_3_ms': 300},
                          MOCK_LAP_NUMBER: {'car_race_position': 10, 'is_valid': True, 'lap_number': 2, 'pit_status': 2, 'sector_1_ms': 1000, 'sector_2_ms': 543, 'sector_3_ms': None}})
        self.assertEqual(session.telemetry.lap_dict[MOCK_LAP_NUMBER].frame_dict, {2345: [4321, 1543.0, None, None, None, None, None, None]})
        self.assertEqual(session.complete_lap_v2.call_count, 1)

    def test_update_current_lap(self):
        session = F12021Session(123)
        session.start_new_lap(MOCK_LAP_NUMBER)
        packet = MockPacketLapData()
        session = packet.update_current_lap(session)
        self.assertEqual(session.lap_list, 
                         {MOCK_LAP_NUMBER: {'car_race_position': 10, 'is_valid': True, 'lap_number': 2, 'pit_status': 2, 'sector_1_ms': 1000, 'sector_2_ms': 543, 'sector_3_ms': None}})
        packet.lapData[0].currentLapInvalid = 1
        packet.lapData[0].carPosition = 9
        packet.lapData[0].pitStatus = 0
        packet.lapData[0].currentLapTimeInMS = 2000
        session = packet.update_current_lap(session)
        self.assertEqual(session.lap_list, 
                         {MOCK_LAP_NUMBER: {'car_race_position': 9, 'is_valid': False, 'lap_number': 2, 'pit_status': 2, 'sector_1_ms': 1000, 'sector_2_ms': 543, 'sector_3_ms': 457}})

    def test_update_telemetry(self):
        session = F12021Session(123)
        session.telemetry.start_new_lap(MOCK_LAP_NUMBER)
        packet = MockPacketLapData()
        # Revert back to default, other tests might have overwritten it
        packet.lapData[0].currentLapTimeInMS = 1543
        session = packet.update_telemetry(session)
        self.assertEqual(session.telemetry.lap_dict[MOCK_LAP_NUMBER].frame_dict, {2345: [4321, 1543.0, None, None, None, None, None, None]})


if __name__ == '__main__':
    unittest.main()


class MockLapData(LapData):
    currentLapNum = MOCK_LAP_NUMBER
    carPosition = 10
    pitStatus = 2
    currentLapInvalid = 0
    currentLapTimeInMS = 1543
    lapDistance = 4321
    sector1TimeInMS = 1000
    sector2TimeInMS = 543
    lastLapTimeInMS = 1200


class MockPacketLapData(PacketLapData):
    header = MagicMock(playerCarIndex=0, frameIdentifier=2345)
    lapData = [MockLapData, ]

