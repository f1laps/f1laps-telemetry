import ctypes


def packet_representation(packet):
    fstr_list = []
    for field in packet._fields_:
        fname = field[0]
        value = getattr(packet, fname)
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
    return "{}({})".format(packet.__class__.__name__, ", ".join(fstr_list))