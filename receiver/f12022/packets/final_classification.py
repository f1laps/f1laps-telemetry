import ctypes

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
        ("tyreStintsEndLaps", ctypes.c_uint8 * 8),
    ]


class PacketFinalClassificationData(PacketBase):
    _fields_ = [
        ("header", PacketHeader),  # Header
        ("numCars", ctypes.c_uint8),  # Number of cars in the final classification
        ("classificationData", FinalClassificationData * 22),
    ]

    def serialize(self):
        try:
            classification_data = self.classificationData[self.header.playerCarIndex]
        except:
            return None
        serialized_dict = {
            "packet_type": "final_classification",
            "finish_position": classification_data.position,
            "result_status": classification_data.resultStatus,
            "points": classification_data.points,
            "all_participants_results": {}
        }
        # Add results of each participant to all_participants_results, indexed by index
        for index, classification in enumerate(self.classificationData):
            serialized_dict["all_participants_results"][index] = {
                "finish_position": classification.position,
                "result_status": classification.resultStatus,
                "points": classification.points,
                "grid_position": classification.gridPosition,
                "lap_time_best": classification.bestLapTimeInMS,
                "penalties_number": classification.numPenalties,
                "race_time_total": int(classification.totalRaceTime*1000) if classification.totalRaceTime else None,
                "penalties_time_total": int(classification.penaltiesTime*1000) if classification.penaltiesTime else None,
            }
            # Set user best lap time in main dict too
            if index == self.header.playerCarIndex:
                serialized_dict["user_lap_time_best"] = classification.bestLapTimeInMS
        return serialized_dict
