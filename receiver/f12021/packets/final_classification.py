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
        # Update user's results in session
        self.set_results(session)
        # Update all participants in session array
        self.update_participants(session)
        session.complete_session()
        return session

    def set_results(self, session):
        try:
            classification_data = self.classificationData[self.header.playerCarIndex]
        except:
            return
        session.finish_position = classification_data.position
        session.result_status   = classification_data.resultStatus
        session.points          = classification_data.points

    def update_participants(self, session):
        num_participants = len(session.participants)
        for index, classification in enumerate(self.classificationData):
            index_real_count = index+1 # +1 because 0-indexing -- for comparison and logging purposes only
            if index_real_count > num_participants:   
                # This should never happen
                log.warning("Classification count of %s (or more) is higher than participant count of %s" % (index_real_count, num_participants))
                break
            participant = session.participants[index]
            participant.points = classification.points
            participant.finish_position = classification.position
            participant.result_status = classification.resultStatus
            participant.lap_time_best = classification.bestLapTimeInMS
            participant.race_time_total = classification.totalRaceTime
            participant.penalties_time_total = classification.penaltiesTime



