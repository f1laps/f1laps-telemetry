import ctypes

from receiver.game_version import CrossGamePacketHeader


class PacketBase(ctypes.LittleEndianStructure):
    _pack_ = 1

    def process(self, session):
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