from unittest import TestCase
from unittest.mock import MagicMock

from receiver.f12021.packets.event import PacketEventData, EventDataDetails, FlashbackData, PenaltyData
from receiver.f12021.session import F12021Session
from receiver.game_version import CrossGamePacketHeader


class PacketEventDataTest(TestCase):

    def test_process_flashback(self):
        session = MagicMock()
        packet = MockPacketFlashbackEventData()
        session = packet.process(session)
        self.assertEqual(session.telemetry.process_flashback_event.call_count, 1)
        session.telemetry.process_flashback_event.assert_called_with(113)
    
    def test_process_penalty(self):
        session = F12021Session(123)
        session.start_new_lap(3)
        packet = MockPacketPenaltyEventData()
        # Calling the submethod to verify penalty
        packet.process_pentalty(session)
        penalty = session.lap_list[3]["penalties"][0]
        self.assertEqual(penalty.penalty_type, 5)
        self.assertEqual(penalty.lap_number, 3)
        self.assertEqual(penalty.frame_id, 123)

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
class MockPenaltyData(PenaltyData):
    penaltyType = 5 # Warning
    infringementType = 7 # Corner cutting 
    vehicleIdx = 1
    otherVehicleIdx = 0
    time = 0
    lapNum = 3 
    placesGained = 0

class MockPenaltyEventDataDetails(EventDataDetails):
    penalty = MockPenaltyData

class MockHeader(CrossGamePacketHeader):
    packetFormat = 2021
    gameMajorVersion = 1
    gameMinorVersion = 1
    packetVersion = 1
    packetId = 1
    sessionUID = 1
    sessionTime = 1
    frameIdentifier = 123
    playerCarIndex = 1
    secondaryPlayerCarIndex = 1

class MockPacketPenaltyEventData(PacketEventData):
    header = MockHeader
    eventStringCode = b"PENA"
    eventDetails = MockPenaltyEventDataDetails