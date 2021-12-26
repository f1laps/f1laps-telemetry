from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12021.packets.event import PacketEventData, EventDataDetails, FlashbackData
from receiver.f12021.penalty import F12021Penalty


class PacketEventDataTest(TestCase):

    def test_process_flashback(self):
        session = MagicMock()
        packet = MockPacketFlashbackEventData()
        session = packet.process(session)
        self.assertEqual(session.telemetry.process_flashback_event.call_count, 1)
        session.telemetry.process_flashback_event.assert_called_with(113)
    
    @patch('receiver.f12021.packets.event.F12021Penalty')
    def test_process_penalty(self, patch_penalty):
        session = MagicMock()
        packet = MockPacketPenaltyEventData()
        # Calling the submethod to verify penalty
        penalty = packet.process_pentalty(session)
        self.assertEqual(penalty.penalty_type, 5)
        self.assertEqual(penalty.lap_number, 3)
        self.assertEqual(penalty.send_to_f1laps.call_count, 1)

    def test_process_unsupported_event(self):
        session = MagicMock()
        packet = MockPacketFlashbackEventData()
        packet.eventStringCode = b"VETL"
        session = packet.process(session)
        self.assertEqual(session.telemetry.process_flashback_event.call_count, 0)


if __name__ == '__main__':
    unittest.main()


###### Flashback
class MockFlashbackData(FlashbackData):
    flashbackFrameIdentifier = 113
    flashbackSessionTime = 34.567

class MockFlashbackEventDataDetails(EventDataDetails):
    flashback = MockFlashbackData

class MockPacketFlashbackEventData(PacketEventData):
    header = MagicMock()
    eventStringCode = b"FLBK"
    eventDetails = MockFlashbackEventDataDetails

###### Penalty
class MockPenaltyData(FlashbackData):
    penaltyType = 5 # Warning
    infringementType = 7 # Corner cutting 
    vehicleIdx = 1
    otherVehicleIdx = 0
    time = 0
    lapNum = 3 
    placesGained = 0

class MockPenaltyEventDataDetails(EventDataDetails):
    penalty = MockPenaltyData

class MockPacketPenaltyEventData(PacketEventData):
    header = MagicMock()
    eventStringCode = b"PENA"
    eventDetails = MockPenaltyEventDataDetails
