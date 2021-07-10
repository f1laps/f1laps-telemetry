import ctypes

from lib.logger import log
from .base import PacketBase, PacketHeader


class LapHistoryData(PacketBase):
    _fields_ = [
        ("lapTimeInMS", ctypes.c_uint32),
        ("sector1TimeInMS", ctypes.c_uint16),
        ("sector2TimeInMS", ctypes.c_uint16),
        ("sector3TimeInMS", ctypes.c_uint16),
        ("lapValidBitFlags", ctypes.c_uint8),
        # 0x01 bit set-lap valid,      0x02 bit set-sector 1 valid
        # 0x04 bit set-sector 2 valid, 0x08 bit set-sector 3 valid
    ]


class TyreStintsHistoryData(PacketBase):
    _fields_ = [
        ("endLap", ctypes.c_uint8),
        ("tyreActualCompound", ctypes.c_uint8), # Actual tyres used by this driver
        ("tyreVisualCompound", ctypes.c_uint8), # Visual tyres used by this driver
    ]


class PacketSessionHistoryData(PacketBase):
    """
    This packet contains lap times and tyre usage for the session. 
    This packet works slightly differently to other packets. 
    To reduce CPU and bandwidth, each packet relates to a specific vehicle and is sent every 1/20 s, 
    and the vehicle being sent is cycled through. 
    Therefore in a 20 car race you should receive an update for each vehicle at least once per second.
    """
    _fields_ = [
        ("header", PacketHeader),  # Header
        ("carIdx", ctypes.c_uint8),  # Index of the car this lap data relates to
        ("numLaps", ctypes.c_uint8),  # Num laps in the data (including current partial lap)
        ("numTyreStints", ctypes.c_uint8),  # Number of tyre stints in the data
        ("bestLapTimeLapNum", ctypes.c_uint8),  # Lap the best lap time was achieved on
        ("bestSector1LapNum", ctypes.c_uint8),  # Lap the best Sector 1 time was achieved on
        ("bestSector2LapNum", ctypes.c_uint8),  # Lap the best Sector 2 time was achieved on
        ("bestSector3LapNum", ctypes.c_uint8),  # Lap the best Sector 3 time was achieved on
        ("lapHistoryData", LapHistoryData * 100),
        ("tyreStintsHistoryData", TyreStintsHistoryData * 8),
    ]

    def process(self, session):
        if not self.is_current_player():
            return session
        session = self.update_laps(session)
        return session

    def update_laps(self, session):
        num_laps = self.numLaps
        if not num_laps:
            return session
        # loop through existing laps and add them to local dict
        # only if > 1 because 1 is always the current, incomplete lap
        if num_laps > 1:
            lap_dict = session.lap_list
            for lap_number in range(1, num_laps):
                # Complete lap if it doesnt exist or if sector 3 time isnt set
                # S3 time is a proxy for "did we complete it before"
                # May have to make this more explicit in the future
                if lap_number not in lap_dict or lap_dict[lap_number].get("sector_3_ms") is None:
                    udp_lap_data = self.lapHistoryData[lap_number-1]
                    sector_1_ms, sector_2_ms, sector_3_ms = self.clean_sectors(udp_lap_data)
                    session.complete_lap(
                        lap_number = lap_number,
                        sector_1_ms = sector_1_ms,
                        sector_2_ms = sector_2_ms,
                        sector_3_ms = sector_3_ms,
                        tyre_visual = self.get_tyre_visual(lap_number)
                        )
                    log.debug("Lap History: T %s S1 %s S2 %s S3 %s" % (
                        udp_lap_data.lapTimeInMS,
                        udp_lap_data.sector1TimeInMS,
                        udp_lap_data.sector2TimeInMS,
                        udp_lap_data.sector3TimeInMS
                        ))
                    log.debug("Updated lap dict to %s" % session.lap_list)
        return session

    def clean_sectors(self, udp_lap_data):
        laptime = udp_lap_data.lapTimeInMS
        sector_1_ms = udp_lap_data.sector1TimeInMS
        sector_2_ms = udp_lap_data.sector2TimeInMS
        sector_3_ms = udp_lap_data.sector3TimeInMS
        lap_sector_delta = laptime - sector_1_ms - sector_2_ms - sector_3_ms
        if lap_sector_delta < 0:
            sector_1_ms = sector_1_ms - 1
            if lap_sector_delta < -1:
                sector_2_ms = sector_2_ms - 1
                if lap_sector_delta < -2:
                    sector_3_ms = sector_3_ms - 1
        if lap_sector_delta > 0:
            sector_1_ms = sector_1_ms + 1
            if lap_sector_delta > 1:
                sector_2_ms = sector_2_ms + 1
                if lap_sector_delta > 2:
                    sector_3_ms = sector_3_ms + 1
        return sector_1_ms, sector_2_ms, sector_3_ms
            

    def is_current_player(self):
        return self.carIdx == self.header.playerCarIndex

    def get_tyre_visual(self, lap_number):
        for tyre_stint in self.tyreStintsHistoryData:
            if lap_number <= tyre_stint.endLap:
                return tyre_stint.tyreVisualCompound

