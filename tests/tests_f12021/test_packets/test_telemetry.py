from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12021.packets.telemetry import CarTelemetryData, PacketCarTelemetryData
from receiver.f12021.session import F12021Session


class PacketCarTelemetryDataTest(TestCase):

    def test_update_telemetry(self):
        session = F12021Session(123)
        session.telemetry.start_new_lap(1)
        packet = MockPacketCarTelemetryData()
        session = packet.update_telemetry(session)
        self.assertEqual(session.telemetry.lap_dict[1].frame_dict, {2345: [None, None, 111, 0, 0.82, 6, 0.21, 0]})


if __name__ == '__main__':
    unittest.main()


class MockCarTelemetryData(CarTelemetryData):
    speed = 111
    throttle = 0.82
    steer = 0.21
    brake = 0
    gear = 6
    drs = 0


class MockPacketCarTelemetryData(PacketCarTelemetryData):
    header = MagicMock(playerCarIndex=0, frameIdentifier=2345)
    carTelemetryData = [MockCarTelemetryData, ]

