import ctypes

from lib.logger import log
from receiver.game_version import CrossGamePacketHeader
from lib.packets.representation import packet_representation


class PacketBase(ctypes.LittleEndianStructure):
    _pack_ = 1
    creates_session_object = False

    def process(self, session):
        log.debug("Skipping incoming %s because it doesn't have a '.process()' method" % self.__class__.__name__)
        return session

    def __repr__(self):
        """ Custom repr method """
        return packet_representation(self)


class PacketHeader(CrossGamePacketHeader):
    """ 
    The Packet Header is the same across F12020 and F12021
    Hence we use one shared HeaderClass for now
    May have to upgrade that logic if it changes
    """
    pass