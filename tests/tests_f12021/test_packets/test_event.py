from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12021.packets.event import PacketEventData, EventDataDetails, FlashbackData
from receiver.f12021.session import F12021Session


class PacketEventDataTest(TestCase):

    def test_process(self):
        session = MagicMock()
        packet = MockPacketEventData()
        session = packet.process(session)
        self.assertEqual(session.telemetry.process_flashback_event.call_count, 1)
        session.telemetry.process_flashback_event.assert_called_with(113)

    def test_process_unsupported_event(self):
        session = MagicMock()
        packet = MockPacketEventData()
        packet.eventStringCode = b"VETL"
        session = packet.process(session)
        self.assertEqual(session.telemetry.process_flashback_event.call_count, 0)


if __name__ == '__main__':
    unittest.main()


class MockFlashbackData(FlashbackData):
    flashbackFrameIdentifier = 113
    flashbackSessionTime = 34.567


class MockEventDataDetails(EventDataDetails):
    flashback = MockFlashbackData


class MockPacketEventData(PacketEventData):
    header = MagicMock()
    eventStringCode = b"FLBK"
    eventDetails = MockEventDataDetails

