import ctypes

from .base import PacketBase, PacketHeader

class CarDamageData(PacketBase):
    _fields_ = [
        ("tyresWear", ctypes.c_float * 4),
        ("tyresDamage", ctypes.c_int8 * 4),
        ("brakesDamage", ctypes.c_int8 * 4),
        ("frontLeftWingDamage", ctypes.c_int8),
        ("frontRightWingDamage", ctypes.c_int8),
        ("rearWingDamage", ctypes.c_int8),
        ("floorDamage", ctypes.c_int8),
        ("diffuserDamage", ctypes.c_int8),
        ("sidepodDamage", ctypes.c_int8),
        ("drsFault", ctypes.c_int8),
        ("ersFault", ctypes.c_int8),
        ("gearBoxDamage", ctypes.c_int8),
        ("engineDamage", ctypes.c_int8),
        ("engineMGUHWear", ctypes.c_int8),
        ("engineESWear", ctypes.c_int8),
        ("engineCEWear", ctypes.c_int8),
        ("engineICEWear", ctypes.c_int8),
        ("engineMGUKWear", ctypes.c_int8),
        ("engineTCWear", ctypes.c_int8),
        ("engineBlown", ctypes.c_int8),
        ("engineSeized", ctypes.c_int8),
    ]


class PacketCarDamageData(PacketBase):
    """
    This packet details car damage parameters for all the cars in the race.
    Frequency: 2 per second
    Size: 948 bytes
    Version: 1
    """

    _fields_ = [
        ("header", PacketHeader), 
        ("carDamageData", CarDamageData * 22),
    ]

    def serialize(self):
        try:
            car_damage = self.carDamageData[self.header.playerCarIndex]
        except:
            return None
        return {
            "packet_type": "car_damage",
            "tyre_wear_front_left": car_damage.tyresWear[2],
            "tyre_wear_front_right": car_damage.tyresWear[3],
            "tyre_wear_rear_left": car_damage.tyresWear[0],
            "tyre_wear_rear_right": car_damage.tyresWear[1]
        }