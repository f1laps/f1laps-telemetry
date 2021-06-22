from receiver.telemetry_base import TelemetryBase, TelemetryLapBase


class Telemetry(TelemetryBase):
    TelemetryLapModel = TelemetryLap


class TelemetryLap(TelemetryLapBase):
    pass