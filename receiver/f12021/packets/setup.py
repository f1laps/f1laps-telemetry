import ctypes

from .base import PacketBase, PacketHeader
from .base import CAR_INDEX

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

    def process(self, session):
        return self.update_setup(session)

    def update_setup(self, session):
        try:
            setup_data = self.carSetups[CAR_INDEX]
        except:
            return session
        session.setup['front_wing']                   = setup_data.frontWing
        session.setup['rear_wing']                    = setup_data.rearWing
        session.setup['diff_adjustment_on_throttle']  = setup_data.onThrottle
        session.setup['diff_adjustment_off_throttle'] = setup_data.offThrottle
        session.setup['front_camber']                 = setup_data.frontCamber
        session.setup['rear_camber']                  = setup_data.rearCamber
        session.setup['front_toe']                    = setup_data.frontToe
        session.setup['rear_toe']                     = setup_data.rearToe
        session.setup['front_suspension']             = setup_data.frontSuspension
        session.setup['rear_suspension']              = setup_data.rearSuspension
        session.setup['front_antiroll_bar']           = setup_data.frontAntiRollBar
        session.setup['rear_antiroll_bar']            = setup_data.rearAntiRollBar
        session.setup['front_ride_height']            = setup_data.frontSuspensionHeight
        session.setup['rear_ride_height']             = setup_data.rearSuspensionHeight
        session.setup['brake_pressure']               = setup_data.brakePressure
        session.setup['front_brake_bias']             = setup_data.brakeBias
        session.setup['front_right_tyre_pressure']    = setup_data.frontRightTyrePressure
        session.setup['front_left_tyre_pressure']     = setup_data.frontLeftTyrePressure
        session.setup['rear_right_tyre_pressure']     = setup_data.rearRightTyrePressure
        session.setup['rear_left_tyre_pressure']      = setup_data.rearLeftTyrePressure
        return session
        