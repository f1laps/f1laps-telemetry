import ctypes

from lib.logger import log
from .base import PacketBase, PacketHeader


class FlashbackData(PacketBase):
    """Event data for Flashback activated (FLBK)"""

    _fields_ = [
        ("flashbackFrameIdentifier", ctypes.c_uint32),  # Frame identifier flashed back to
        ("flashbackSessionTime", ctypes.c_float),  # Session time flashed back to
    ]


class EventDataDetails(ctypes.Union):
    """Union for the different event data types"""

    _fields_ = [
        ("flashback", FlashbackData),
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
        if self.eventStringCode == "FLBK":
            log.inf0("*******************")
            log.info("Received FLBK event")
            log.info("eventDets: %s" % self.eventDetails)
            log.info("frameID: %s" % self.eventDetails.flashbackFrameIdentifier)
            log.info("sessionTime: %s" % self.eventDetails.flashbackSessionTime)
            log.inf0("*******************")
        return session
