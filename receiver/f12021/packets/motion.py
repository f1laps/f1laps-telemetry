import ctypes

from .base import PacketBase, PacketHeader

MINIMAP_ROUNDING = 0
MINIMAP_SPACING_M = 1


class CarMotionData(PacketBase):
    _fields_ = [
        ("worldPositionX", ctypes.c_float),
        ("worldPositionY", ctypes.c_float),
        ("worldPositionZ", ctypes.c_float),
        ("worldVelocityX", ctypes.c_float),
        ("worldVelocityY", ctypes.c_float),
        ("worldVelocityZ", ctypes.c_float),
        ("worldForwardDirX", ctypes.c_int16),
        ("worldForwardDirY", ctypes.c_int16),
        ("worldForwardDirZ", ctypes.c_int16),
        ("worldRightDirX", ctypes.c_int16),
        ("worldRightDirY", ctypes.c_int16),
        ("worldRightDirZ", ctypes.c_int16),
        ("gForceLateral", ctypes.c_float),
        ("gForceLongitudinal", ctypes.c_float),
        ("gForceVertical", ctypes.c_float),
        ("yaw", ctypes.c_float),
        ("pitch", ctypes.c_float),
        ("roll", ctypes.c_float),
    ]


class PacketMotionData(PacketBase):
    """
    The motion packet gives physics data for all the cars being driven. There is additional data for the car being driven with the goal of being able to drive a motion platform setup.
    N.B. For the normalised vectors below, to convert to float values divide by 32767.0f – 16-bit signed values are used to pack the data and on the assumption that direction values are always between -1.0f and 1.0f.
    Frequency: Rate as specified in menus
    Size: 1464 bytes
    Version: 1
    """

    _fields_ = [
        ("header", PacketHeader), 
        ("carMotionData", CarSetupData * 22),
        ("suspensionPosition", ctypes.c_float * 4),
        ("suspensionVelocity", ctypes.c_float * 4),
        ("suspensionAcceleration", ctypes.c_float * 4),
        ("wheelSpeed", ctypes.c_float * 4),
        ("wheelSlip", ctypes.c_float * 4),
        ("localVelocityX", ctypes.c_float),
        ("localVelocityY", ctypes.c_float),
        ("localVelocityZ", ctypes.c_float),
        ("angularVelocityX", ctypes.c_float),
        ("angularVelocityY", ctypes.c_float),
        ("angularVelocityZ", ctypes.c_float),
        ("angularAccelerationX", ctypes.c_float),
        ("angularAccelerationY", ctypes.c_float),
        ("angularAccelerationZ", ctypes.c_float),
        ("frontWheelsAngle", ctypes.c_float),
    ]

    def process(self, session):
        self.update_map_data(session)
        return session

    def update_map_data(self, session):
        try:
            car_motion = self.carMotionData[self.header.playerCarIndex]
        except:
            return None
        xpos = car_motion.worldPositionX
        # ypos = car_motion.worldPositionY # ypos is height
        zpos = car_motion.worldPositionZ
        if xpos and zpos and session.lap_distance:
            if not session.last_logged_distance:
                log.info("WPMAP: %s,%s,%s" % (
                    round(session.lap_distance, MINIMAP_ROUNDING), 
                    round(xpos, MINIMAP_ROUNDING), 
                    round(zpos, MINIMAP_ROUNDING)
                ))
                session.last_logged_distance = session.lap_distance
            else:
                spacing = session.lap_distance - session.last_logged_distance
                if spacing < 0 or spacing > MINIMAP_SPACING_M:
                    log.info("WPMAP: %s,%s,%s" % (
                        round(session.lap_distance, MINIMAP_ROUNDING), 
                        round(xpos, MINIMAP_ROUNDING), 
                        round(zpos, MINIMAP_ROUNDING)
                    ))
                    session.last_logged_distance = session.lap_distance
        return session
        