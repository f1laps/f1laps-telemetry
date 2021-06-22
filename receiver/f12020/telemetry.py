from receiver.telemetry_base import TelemetryBase, TelemetryLapBase


class TelemetryLap(TelemetryLapBase):
    pass


class Telemetry(TelemetryBase):
    TelemetryLapModel = TelemetryLap