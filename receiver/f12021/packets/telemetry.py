import ctypes

from .base import PacketBase, PacketHeader

from .base import CAR_INDEX

class CarTelemetryData(PacketBase):
    _fields_ = [
        ("speed", ctypes.c_uint16),
        ("throttle", ctypes.c_float),
        ("steer", ctypes.c_float),
        ("brake", ctypes.c_float),
        ("clutch", ctypes.c_uint8),
        ("gear", ctypes.c_int8),
        ("engineRPM", ctypes.c_uint16),
        ("drs", ctypes.c_uint8),
        ("revLightsPercent", ctypes.c_uint8),
        ("revLightsBitValue", ctypes.c_uint16),
        ("brakesTemperature", ctypes.c_uint16 * 4),
        ("tyresSurfaceTemperature", ctypes.c_uint8 * 4),
        ("tyresInnerTemperature", ctypes.c_uint8 * 4),
        ("engineTemperature", ctypes.c_uint16),
        ("tyresPressure", ctypes.c_float * 4),
        ("surfaceType", ctypes.c_uint8 * 4),
    ]


class PacketCarTelemetryData(PacketBase):
    """
    This packet details telemetry for all the cars in the race.
    It details various values that would be recorded on the car such as speed, throttle application, DRS etc.
    Frequency: Rate as specified in menus
    Size: 1351 bytes
    Version: 1
    """

    _fields_ = [
        ("header", PacketHeader),
        ("carTelemetryData", CarTelemetryData * 22),
        ("mfdPanelIndex", ctypes.c_uint8),
        ("mfdPanelIndexSecondaryPlayer", ctypes.c_uint8),
        ("suggestedGear", ctypes.c_int8),
    ]

    def process(self, session):
        session = self.update_telemetry(session)
        return session

    def update_telemetry(self, session):
        try:
            telemetry_data = self.carTelemetryData[CAR_INDEX]
        except:
            return None
        frame = self.header.frameIdentifier
        session.telemetry.set(frame, speed    = telemetry_data.speed,
                                     brake    = telemetry_data.brake,
                                     throttle = telemetry_data.throttle,
                                     gear     = telemetry_data.gear,
                                     steer    = telemetry_data.steer,
                                     drs      = telemetry_data.drs)
        return session

