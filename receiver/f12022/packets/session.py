import ctypes
import logging
log = logging.getLogger(__name__)

from .base import PacketBase, PacketHeader


class MarshalZone(PacketBase):
    _fields_ = [("zoneStart", ctypes.c_float), ("zoneFlag", ctypes.c_int8)]


class WeatherForecastSample(PacketBase):
    _fields_ = [
        ("sessionType", ctypes.c_uint8),
        ("timeOffset", ctypes.c_uint8),
        ("weather", ctypes.c_uint8),
        ("trackTemperature", ctypes.c_int8),
        ("trackTemperatureChange", ctypes.c_int8),
        ("airTemperature", ctypes.c_int8),
        ("airTemperatureChange", ctypes.c_int8),
        ("rainPercentage", ctypes.c_uint8),
    ]


class PacketSessionData(PacketBase):
    creates_session_object = True
    _fields_ = [
        ("header", PacketHeader),
        ("weather", ctypes.c_uint8),
        ("trackTemperature", ctypes.c_int8),
        ("airTemperature", ctypes.c_int8),
        ("totalLaps", ctypes.c_uint8),
        ("trackLength", ctypes.c_uint16),
        ("sessionType", ctypes.c_uint8), 
        # 0 = unknown, 1 = P1, 2 = P2, 3 = P3, 4 = Short P
        # 5 = Q1, 6 = Q2, 7 = Q3, 8 = Short Q, 9 = OSQ
        # 10 = R, 11 = R2, 12 = R3, 13 = Time Trial
        ("trackId", ctypes.c_int8),
        ("formula", ctypes.c_uint8),
        # 0 = F1 Modern, 1 = F1 Classic, 2 = F2,
        # 3 = F1 Generic, 4 = Beta, 5 = Supercars    
        ("sessionTimeLeft", ctypes.c_uint16),
        ("sessionDuration", ctypes.c_uint16),
        ("pitSpeedLimit", ctypes.c_uint8),
        ("gamePaused", ctypes.c_uint8),
        ("isSpectating", ctypes.c_uint8),
        ("spectatorCarIndex", ctypes.c_uint8),
        ("sliProNativeSupport", ctypes.c_uint8),
        ("numMarshalZones", ctypes.c_uint8),
        ("marshalZones", MarshalZone * 21),
        ("safetyCarStatus", ctypes.c_uint8),
        ("networkGame", ctypes.c_uint8),
        ("numWeatherForecastSamples", ctypes.c_uint8),
        ("weatherForecastSamples", WeatherForecastSample * 56),
        ("forecastAccuracy", ctypes.c_uint8),
        ("aiDifficulty", ctypes.c_uint8), # AI Difficulty rating – 0-110
        ("seasonLinkIdentifier", ctypes.c_uint32),
        ("weekendLinkIdentifier", ctypes.c_uint32),
        ("sessionLinkIdentifier", ctypes.c_uint32),
        ("pitStopWindowIdealLap", ctypes.c_uint8),
        ("pitStopWindowLatestLap", ctypes.c_uint8),
        ("pitStopRejoinPosition", ctypes.c_uint8),
        ("steeringAssist", ctypes.c_uint8),
        ("brakingAssist", ctypes.c_uint8),
        ("gearboxAssist", ctypes.c_uint8),
        ("pitAssist", ctypes.c_uint8),
        ("pitReleaseAssist", ctypes.c_uint8),
        ("ERSAssist", ctypes.c_uint8),
        ("DRSAssist", ctypes.c_uint8),
        ("dynamicRacingLine", ctypes.c_uint8),
        ("dynamicRacingLineType", ctypes.c_uint8),
        ("gameMode", ctypes.c_uint8),
        ("ruleSet", ctypes.c_uint8),
        ("timeOfDay", ctypes.c_uint32),
        ("sessionLength", ctypes.c_uint8),
        # 0 = None, 2 = Very Short, 3 = Short, 4 = Medium
        # 5 = Medium Long, 6 = Long, 7 = Full
    ]

    def serialize(self):
        serialized_packet = {
            "packet_type": "session",
            "session_uid": self.header.sessionUID,
            "session_type": self.sessionType,
            "track_id": self.trackId,
            "is_online_game": bool(self.networkGame == 1),
            "ai_difficulty": self.aiDifficulty,
            "weather_id": self.weather,
            "is_spectating": self.isSpectating,
            "game_mode": self.gameMode,
            "season_link_identifier": self.seasonLinkIdentifier,
            "track_temperature": self.trackTemperature,
            "air_temperature": self.airTemperature,
            "rain_percentage_forecast": None,
        }
        # Add rain percentage from last weather forecast sample, if any exist
        if self.numWeatherForecastSamples > 0:
            serialized_packet["rain_percentage_forecast"] = self.weatherForecastSamples[
                self.numWeatherForecastSamples - 1
            ].rainPercentage
        return serialized_packet


