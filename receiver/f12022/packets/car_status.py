import ctypes

from .base import PacketBase, PacketHeader


class CarStatusData(PacketBase):
    """
    There is some data in the Car Status packets that you may not want other players seeing if you are in a multiplayer game.
    This is controlled by the "Your Telemetry" setting in the Telemetry options. The options are:
        Restricted (Default) – other players viewing the UDP data will not see values for your car;
        Public – all other players can see all the data for your car.
    Note: You can always see the data for the car you are driving regardless of the setting.
    The following data items are set to zero if the player driving the car in question has their "Your Telemetry" set to "Restricted":
        fuelInTank, fuelCapacity, fuelMix, fuelRemainingLaps, frontBrakeBias, frontLeftWingDamage, frontRightWingDamage, rearWingDamage, 
        engineDamage, gearBoxDamage, tyresWear (All four wheels), tyresDamage (All four wheels), ersDeployMode, ersStoreEnergy, 
        ersDeployedThisLap, ersHarvestedThisLapMGUK, ersHarvestedThisLapMGUH, tyresAgeLaps
    """
    _fields_ = [
        ("tractionControl", ctypes.c_uint8),
        ("antiLockBrakes", ctypes.c_uint8),
        ("fuelMix", ctypes.c_uint8),
        ("frontBrakeBias", ctypes.c_uint8),
        ("pitLimiterStatus", ctypes.c_uint8),
        ("fuelInTank", ctypes.c_float),
        ("fuelCapacity", ctypes.c_float),
        ("fuelRemainingLaps", ctypes.c_float),
        ("maxRPM", ctypes.c_uint16),
        ("idleRPM", ctypes.c_uint16),
        ("maxGears", ctypes.c_uint8),
        ("drsAllowed", ctypes.c_uint8),
        ("drsActivationDistance", ctypes.c_uint16),
        ("actualTyreCompound", ctypes.c_uint8),
        ("visualTyreCompound", ctypes.c_uint8),
        ("tyresAgeLaps", ctypes.c_uint8),
        ("vehicleFiaFlags", ctypes.c_int8),
        ("ersStoreEnergy", ctypes.c_float),
        ("ersDeployMode", ctypes.c_uint8),
        ("ersHarvestedThisLapMGUK", ctypes.c_float),
        ("ersHarvestedThisLapMGUH", ctypes.c_float),
        ("ersDeployedThisLap", ctypes.c_float),
        ("networkPaused", ctypes.c_uint8),
    ]



class PacketCarStatusData(PacketBase):
    """
    This packet details car statuses for all the cars in the race.
    It includes values such as the damage readings on the car.
    Frequency: Rate as specified in menus
    Size: 1344 bytes
    """
    _fields_ = [
        ("header", PacketHeader),
        ("carStatusData", CarStatusData * 22),
    ]

    def serialize(self):
        try:
            car_status = self.carStatusData[self.header.playerCarIndex]
        except:
            return None
        return {
            "packet_type": "car_status",
            "tyre_compound_visual": car_status.visualTyreCompound
        }
