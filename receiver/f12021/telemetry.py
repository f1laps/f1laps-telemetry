from receiver.telemetry_base import TelemetryBase, TelemetryLapBase


class F12021TelemetryLap(TelemetryLapBase):
    pass


class F12021Telemetry(TelemetryBase):
    TelemetryLapModel = F12021TelemetryLap