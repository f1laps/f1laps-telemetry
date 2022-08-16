import ctypes
import logging
log = logging.getLogger(__name__)

from .base import PacketBase, PacketHeader
from receiver.f12021.penalty import F12021Penalty


class FlashbackData(PacketBase):
    """Event data for Flashback activated (FLBK)"""

    _fields_ = [
        ("flashbackFrameIdentifier", ctypes.c_uint32),  # Frame identifier flashed back to
        ("flashbackSessionTime", ctypes.c_float),  # Session time flashed back to
    ]


class PenaltyData(PacketBase):
    """Event data for Penalties (PENA)"""

    _fields_ = [
        ("penaltyType", ctypes.c_uint8),  # Penalty type – see Appendices
        ("infringementType", ctypes.c_uint8),  # Infringement type – see Appendices
        ("vehicleIdx", ctypes.c_uint8),  # Vehicle index of the car the penalty is applied to
        ("otherVehicleIdx", ctypes.c_uint8),  # Vehicle index of the other car involved
        ("time", ctypes.c_uint8),  # Time gained, or time spent doing action in seconds
        ("lapNum", ctypes.c_uint8),  # Lap the penalty occurred on
        ("placesGained", ctypes.c_uint8),  # Number of places gained by this
    ]


class EventDataDetails(ctypes.Union):
    """Union for the different event data types"""

    _fields_ = [
        ("flashback", FlashbackData),
        ("penalty", PenaltyData),
    ]


class PacketEventData(PacketBase):
    """
    This packet gives details of events that happen during the course of a session.
    Frequency: When the event occurs
    Size: 36 bytes
    Version: 1
    """

    _fields_ = [
        ("header", PacketHeader), 
        ("eventStringCode", ctypes.c_char * 4),
        ("eventDetails", EventDataDetails)
    ]

    def process(self, session):
        if self.eventStringCode == b"FLBK":
            self.process_flashback(session)
        elif self.eventStringCode == b"PENA":
            self.process_pentalty(session)
        return session
    
    def process_flashback(self, session):
        frame_id = self.eventDetails.flashback.flashbackFrameIdentifier
        session_time = self.eventDetails.flashback.flashbackSessionTime
        log.info("Event: Flashback happened to frame %s and session time %s. Deleting frames." % (frame_id, session_time))
        session.telemetry.process_flashback_event(frame_id)
    
    def process_pentalty(self, session):
        penalty = F12021Penalty()
        penalty.penalty_type = self.eventDetails.penalty.penaltyType
        penalty.infringement_type = self.eventDetails.penalty.infringementType
        penalty.vehicle_index = self.eventDetails.penalty.vehicleIdx
        penalty.other_vehicle_index = self.eventDetails.penalty.otherVehicleIdx
        penalty.time_spent_gained = self.eventDetails.penalty.time
        penalty.lap_number = self.eventDetails.penalty.lapNum
        penalty.places_gained = self.eventDetails.penalty.placesGained
        penalty.session = session
        penalty.frame_id = self.header.frameIdentifier
        log.info("Processing %s" % penalty)
        penalty.add_to_lap()
        return penalty
