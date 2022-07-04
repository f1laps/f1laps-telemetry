import ctypes

from .base import PacketBase, PacketHeader


class CarSetupData(PacketBase):
    _fields_ = [
        ("frontWing", ctypes.c_uint8),
        ("rearWing", ctypes.c_uint8),
        ("onThrottle", ctypes.c_uint8),
        ("offThrottle", ctypes.c_uint8),
        ("frontCamber", ctypes.c_float),
        ("rearCamber", ctypes.c_float),
        ("frontToe", ctypes.c_float),
        ("rearToe", ctypes.c_float),
        ("frontSuspension", ctypes.c_uint8),
        ("rearSuspension", ctypes.c_uint8),
        ("frontAntiRollBar", ctypes.c_uint8),
        ("rearAntiRollBar", ctypes.c_uint8),
        ("frontSuspensionHeight", ctypes.c_uint8),
        ("rearSuspensionHeight", ctypes.c_uint8),
        ("brakePressure", ctypes.c_uint8),
        ("brakeBias", ctypes.c_uint8),
        ("rearLeftTyrePressure", ctypes.c_float),
        ("rearRightTyrePressure", ctypes.c_float),
        ("frontLeftTyrePressure", ctypes.c_float),
        ("frontRightTyrePressure", ctypes.c_float),
        ("ballast", ctypes.c_uint8),
        ("fuelLoad", ctypes.c_float),
    ]


class PacketCarSetupData(PacketBase):
    """
    This packet details the car setups for each vehicle in the session.
    Note that in multiplayer games, other player cars will appear as blank, you will only be able to see your car setup and AI cars.
    Frequency: 2 per second
    Size: 1102 bytes
    Version: 1
    """

    _fields_ = [("header", PacketHeader), ("carSetups", CarSetupData * 22)]

    def serialize(self):
        try:
            setup_data = self.carSetups[self.header.playerCarIndex]
        except:
            return None
        return {
            "packet_type": "setup",
            "front_wing": setup_data.frontWing,
            "rear_wing": setup_data.rearWing,
            "diff_adjustment_on_throttle": setup_data.onThrottle,
            "diff_adjustment_off_throttle": setup_data.offThrottle,
            # Round float values to 2 decimal places
            # Otherwise they come with 20+ decimal places
            "front_camber": round(setup_data.frontCamber, 2) if setup_data.frontCamber else None,
            "rear_camber": round(setup_data.rearCamber, 2) if setup_data.rearCamber else None,
            "front_toe": round(setup_data.frontToe, 2) if setup_data.frontToe else None,
            "rear_toe": round(setup_data.rearToe, 2) if setup_data.rearToe else None,
            "front_suspension": setup_data.frontSuspension,
            "rear_suspension": setup_data.rearSuspension,
            "front_antiroll_bar": setup_data.frontAntiRollBar,
            "rear_antiroll_bar": setup_data.rearAntiRollBar,
            "front_ride_height": setup_data.frontSuspensionHeight,
            "rear_ride_height": setup_data.rearSuspensionHeight,
            "brake_pressure": setup_data.brakePressure,
            "front_brake_bias": setup_data.brakeBias,
            "front_right_tyre_pressure": setup_data.frontRightTyrePressure,
            "front_left_tyre_pressure": setup_data.frontLeftTyrePressure,
            "rear_right_tyre_pressure": setup_data.rearRightTyrePressure,
            "rear_left_tyre_pressure": setup_data.rearLeftTyrePressure,
        }
        