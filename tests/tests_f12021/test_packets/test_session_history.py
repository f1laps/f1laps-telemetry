from unittest import TestCase
from unittest.mock import MagicMock, patch

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

    @patch('receiver.f12021.session.F12021Session.post_process')
    def test_update_laps(self, mock_post_process):
        return True # Disabled
        session = F12021Session(123)
        self.assertEqual(session.lap_list, {})
        packet = MockPacketSessionHistoryData()
        packet.update_laps(session)
        self.assertEqual(session.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 10000, 'sector_2_ms': 20000, 'sector_3_ms': 30000, 'tyre_compound_visual': 16}})
        packet.update_laps(session)
        self.assertEqual(session.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 10000, 'sector_2_ms': 20000, 'sector_3_ms': 30000, 'tyre_compound_visual': 16}})

    @patch('receiver.f12021.session.F12021Session.post_process')
    def test_update_laps_rounding_patch(self, mock_post_process):
        """
        Sometimes the packet's sector times dont add up to the actual lap time
        In this case, we patch it by adjusting sector times so that the final
        lap time matches the game's UI
        """
        return True # Disabled
        session = F12021Session(123)
        packet = MockPacketSessionHistoryData()
        packet.lapHistoryData[0].sector3TimeInMS = 30001
        packet.update_laps(session)
        self.assertEqual(session.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 9999, 'sector_2_ms': 20000, 'sector_3_ms': 30001, 'tyre_compound_visual': 16}})
        session_2 = F12021Session(124)
        packet.lapHistoryData[0].sector1TimeInMS = 10001
        packet.lapHistoryData[0].sector2TimeInMS = 20001
        packet.update_laps(session_2)
        self.assertEqual(session_2.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 10000, 'sector_2_ms': 20000, 'sector_3_ms': 30000, 'tyre_compound_visual': 16}})
        session_3 = F12021Session(125)
        packet.lapHistoryData[0].sector1TimeInMS = 9999
        packet.lapHistoryData[0].sector2TimeInMS = 19999
        packet.lapHistoryData[0].sector3TimeInMS = 29999
        packet.update_laps(session_3)
        self.assertEqual(session_3.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 10000, 'sector_2_ms': 20000, 'sector_3_ms': 30000, 'tyre_compound_visual': 16}})
        session_4 = F12021Session(126)
        packet.lapHistoryData[0].sector1TimeInMS = 10000
        packet.lapHistoryData[0].sector2TimeInMS = 19999
        packet.lapHistoryData[0].sector3TimeInMS = 30000
        packet.update_laps(session_4)
        self.assertEqual(session_4.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 10001, 'sector_2_ms': 19999, 'sector_3_ms': 30000, 'tyre_compound_visual': 16}})
        session_5 = F12021Session(127)
        packet.lapHistoryData[0].lapTimeInMS     = 60001
        packet.lapHistoryData[0].sector1TimeInMS = 10000
        packet.lapHistoryData[0].sector2TimeInMS = 20000
        packet.lapHistoryData[0].sector3TimeInMS = 30000
        packet.update_laps(session_5)
        self.assertEqual(session_5.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 10001, 'sector_2_ms': 20000, 'sector_3_ms': 30000, 'tyre_compound_visual': 16}})
        session_6 = F12021Session(128)
        packet.lapHistoryData[0].lapTimeInMS     = 59997
        packet.lapHistoryData[0].sector1TimeInMS = 10000
        packet.lapHistoryData[0].sector2TimeInMS = 20000
        packet.lapHistoryData[0].sector3TimeInMS = 30000
        packet.update_laps(session_6)
        self.assertEqual(session_6.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 9999, 'sector_2_ms': 19999, 'sector_3_ms': 29999, 'tyre_compound_visual': 16}})

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

