from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12021.packets.car_status import PacketCarStatusData, CarStatusData
from receiver.f12021.session import F12021Session


class PacketParticipantsDataTest(TestCase):

    def test_process(self):
        packet = MockPacketCarStatusData()
        session = F12021Session(123)
        session.start_new_lap(1)
        self.assertEqual(session.lap_list, {1: {}})
        session = packet.process(session)
        self.assertEqual(session.lap_list, {1: {'tyre_compound_visual': 6}})
    


if __name__ == '__main__':
    unittest.main()


class MockCarStatusData(CarStatusData):
    visualTyreCompound = 6


class MockPacketCarStatusData(PacketCarStatusData):
    header = MagicMock(playerCarIndex=0)
    carStatusData = [MockCarStatusData, ]


