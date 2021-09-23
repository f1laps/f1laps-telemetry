import ctypes

from lib.logger import log
from .base import PacketBase, PacketHeader


class FinalClassificationData(PacketBase):
    _fields_ = [
        ("position", ctypes.c_uint8),
        ("numLaps", ctypes.c_uint8),
        ("gridPosition", ctypes.c_uint8),
        ("points", ctypes.c_uint8),
        ("numPitStops", ctypes.c_uint8),
        ("resultStatus", ctypes.c_uint8),
        ("bestLapTimeInMS", ctypes.c_uint32),
        ("totalRaceTime", ctypes.c_double),
        ("penaltiesTime", ctypes.c_uint8),
        ("numPenalties", ctypes.c_uint8),
        ("numTyreStints", ctypes.c_uint8),
        ("tyreStintsActual", ctypes.c_uint8 * 8),
        ("tyreStintsVisual", ctypes.c_uint8 * 8),
    ]


class PacketFinalClassificationData(PacketBase):
    _fields_ = [
        ("header", PacketHeader),  # Header
        ("numCars", ctypes.c_uint8),  # Number of cars in the final classification
        ("classificationData", FinalClassificationData * 22),
    ]

    def process(self, session):
        log.info("FC: start")
        # Update user's results in session
        self.set_results(session)
        log.info("FC: done 1")
        # Update all participants in session array
        self.update_participants(session)
        log.info("FC: done 2")
        session.complete_session()
        log.info("FC: done 3")
        return session

    def set_results(self, session):
        log.info("FC: set_results - start")
        try:
            classification_data = self.classificationData[self.header.playerCarIndex]
        except:
            return
        session.finish_position = classification_data.position
        session.result_status   = classification_data.resultStatus
        session.points          = classification_data.points
        log.info("FC: set_results - set fp to %s" % session.finish_position)

    def update_participants(self, session):
        log.info("FC: update_participants - start")
        num_participants = len(session.participants)
        for index, classification in enumerate(self.classificationData):
            try:
                participant = session.participants[index]
            except:
                continue
            participant.points = classification.points
            participant.finish_position = classification.position
            participant.result_status = classification.resultStatus
            participant.lap_time_best = classification.bestLapTimeInMS
            if classification.totalRaceTime:
                participant.race_time_total = int(classification.totalRaceTime*1000)
            if classification.penaltiesTime:
                participant.penalties_time_total = int(classification.penaltiesTime*1000)
        log.info("FC: update_participants - end")



