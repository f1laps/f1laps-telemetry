from unittest import TestCase
from unittest.mock import MagicMock

from receiver.f12021.packets.session_history import PacketSessionHistoryData, LapHistoryData, TyreStintsHistoryData
from receiver.f12021.session import F12021Session

class PacketSessionHistoryDataTest(TestCase):

    def test_is_current_player(self):
        packet = MockPacketSessionHistoryData()
        self.assertEqual(packet.is_current_player(), True)
        packet.carIdx = 10
        self.assertEqual(packet.is_current_player(), False)

    def test_get_tyre_visual(self):
        packet = MockPacketSessionHistoryData()
        self.assertEqual(packet.get_tyre_visual(1), 16)
        self.assertEqual(packet.get_tyre_visual(2), 17)

    def test_update_laps(self):
        session = F12021Session(123)
        self.assertEqual(session.lap_list, {})
        packet = MockPacketSessionHistoryData()
        packet.update_laps(session)
        self.assertEqual(session.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 10000, 'sector_2_ms': 20000, 'sector_3_ms': 30000, 'tyre_compound_visual': 16}})
        packet.update_laps(session)
        self.assertEqual(session.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 10000, 'sector_2_ms': 20000, 'sector_3_ms': 30000, 'tyre_compound_visual': 16}})

    def test_update_laps_no_initial_update(self):
        session = F12021Session(123)
        self.assertEqual(session.lap_list, {})
        packet = MockPacketSessionHistoryData()
        packet.numLaps = 1
        packet.update_laps(session)
        self.assertEqual(session.lap_list, {})


if __name__ == '__main__':
    unittest.main()


class MockLapHistoryData_1(LapHistoryData):
    lapTimeInMS = 60000
    sector1TimeInMS = 10000
    sector2TimeInMS = 20000
    sector3TimeInMS = 30000

class MockLapHistoryData_2(LapHistoryData):
    lapTimeInMS = 33333
    sector1TimeInMS = 11111
    sector2TimeInMS = 22222
    sector3TimeInMS = 0

class MockTyreStintsHistoryData_1(TyreStintsHistoryData):
    endLap = 1
    tyreActualCompound = 16
    tyreVisualCompound = 16

class MockTyreStintsHistoryData_2(TyreStintsHistoryData):
    endLap = 255
    tyreActualCompound = 17
    tyreVisualCompound = 17

class MockPacketSessionHistoryData(PacketSessionHistoryData):
    header = MagicMock(playerCarIndex=19)
    carIdx = 19
    numLaps = 2
    lapHistoryData = [MockLapHistoryData_1, MockLapHistoryData_2]
    tyreStintsHistoryData = [MockTyreStintsHistoryData_1, MockTyreStintsHistoryData_2]

