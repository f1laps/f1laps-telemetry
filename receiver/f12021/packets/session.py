import ctypes

from lib.logger import log
from receiver.f12021.session import F12021Session
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
    ]

    def process(self, session):
        # if the user is spectating, we don't create a session
        if self.isSpectating:
            log.debug("Spectating mode - no data is synced with F1Laps")
            return None
        if not self.is_active_session(session):
            return self.create_session()
        else:
            return self.update_session(session)

    def is_active_session(self, session):
        session_exists = bool(session)
        if not session_exists:
            log.info("Starting new session because it doesnt exist")
            return False
        udp_id_changed = bool(session.session_udp_uid != self.header.sessionUID)
        if udp_id_changed:
            log.info("Starting new session because UDP changed")
            return False
        return True

    def create_session(self):
        session = F12021Session(session_uid=self.header.sessionUID)
        session.session_udp_uid = self.header.sessionUID
        session.set_session_type(self.sessionType)
        if not self.sessionType:
            log.warning("Got Session packet without sessionType")
        session.track_id = self.trackId
        session.ai_difficulty = self.aiDifficulty
        if self.networkGame == 1:
            session.is_online_game = True
        if self.weather not in session.weather_ids:
            session.weather_ids.append(self.weather)
        session.start()
        log.info("Session vals: season %s weekend %s session %s UID %s" % (
            self.seasonLinkIdentifier,
            self.weekendLinkIdentifier,
            self.sessionLinkIdentifier,
            self.header.sessionUID
            ))
        return session

    def update_session(self, session):
        if self.weather not in session.weather_ids:
            session.weather_ids.append(self.weather)
        session.set_session_type(self.sessionType)
        return session


