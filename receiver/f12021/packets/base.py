import ctypes

from lib.logger import log
from receiver.game_version import CrossGamePacketHeader
from .session import PacketSessionData
from .lap import PacketLapData
from .participants import PacketParticipantsData
from .setup import PacketCarSetupData
from .telemetry import PacketCarTelemetryData
from .final_classification import PacketFinalClassificationData
from .session_history import PacketSessionHistoryData


HeaderFieldsToPacketType = {
     1: PacketSessionData,
     2: PacketLapData,
     4: PacketParticipantsData,
     5: PacketCarSetupData,
     6: PacketCarTelemetryData,
     8: PacketFinalClassificationData,
    11: PacketSessionHistoryData
}


class PacketBase(ctypes.LittleEndianStructure):
    def process(self):
        pass

    def __repr__(self):
        """ Custom repr method """
        fstr_list = []
        for field in self._fields_:
            fname = field[0]
            value = getattr(self, fname)
            if isinstance(
                value, (ctypes.LittleEndianStructure, int, float, bytes)
            ):
                vstr = repr(value)
            elif isinstance(value, ctypes.Array):
                vstr = "[{}]".format(", ".join(repr(e) for e in value))
            else:
                raise RuntimeError(
                    "Bad value {!r} of type {!r}".format(value, type(value))
                )
            fstr = f"{fname}={vstr}"
            fstr_list.append(fstr)
        return "{}({})".format(self.__class__.__name__, ", ".join(fstr_list))


class PacketHeader(CrossGamePacketHeader):
    """ 
    The Packet Header is the same across F12020 and F12021
    Hence we use one shared HeaderClass for now
    May have to upgrade that logic if it changes
    """
    pass


def unpack_udp_packet(packet):
    """
    Important function - processes each packet
    First reads the header, which maps to the right body packet
    Returns the mapped body packet
    """
    header = PacketHeader.from_buffer_copy(packet)
    packet_type = HeaderFieldsToPacketType.get(header.packetId)
    if packet_type:
        return packet_type.from_buffer_copy(packet)
    else:
        log.debug("Received unknown packet_type %s" % packet_type)
        return None
