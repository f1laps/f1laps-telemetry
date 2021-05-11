from unittest import TestCase
from unittest.mock import MagicMock

from receiver.session import Session
from receiver.packets import SessionPacket, LapPacket, FinalClassificationPacket, CarStatusPacket


MOCK_PLAYER_CAR_INDEX = 0

def get_packet_mock():
    packet_header = MagicMock(sessionUID="vettel2021", playerCarIndex=MOCK_PLAYER_CAR_INDEX)
    return MagicMock(header=packet_header, isSpectating=0)


class SessionPacketTest(TestCase):

    def test_session_initial(self):
        packet = get_packet_mock()
        new_session = SessionPacket().process(packet, None)
        self.assertTrue(new_session != None)

    def test_session_existing(self):
        existing_session = Session(session_uid="vettel2021")
        packet = get_packet_mock()
        new_session = SessionPacket().process(packet, existing_session)
        self.assertEqual(new_session, existing_session)

    def test_session_new(self):
        existing_session = Session(session_uid="vettel2021")
        packet = get_packet_mock()
        packet.header.sessionUID = "george2021"
        packet.sessionType = 10
        packet.trackId = 5
        packet.weather = 1
        new_session = SessionPacket().process(packet, existing_session)
        self.assertEqual(new_session.session_udp_uid, "george2021")
        self.assertEqual(new_session.track_id, 5)
        self.assertEqual(new_session.session_type, 10)
        self.assertEqual(new_session.weather_ids, [1])
        self.assertEqual(new_session.is_online_game, False)

    def test_session_new_spectating(self):
        """ Assert that when a user is spectating, no session is created """
        packet = get_packet_mock()
        packet.isSpectating = 1
        new_session = SessionPacket().process(packet, None)
        self.assertEqual(new_session, None)

    def test_session_is_online_game(self):
        """ Assert that an online game gets marked as such """
        packet = get_packet_mock()
        packet.header.sessionUID = "george2021"
        packet.networkGame = 1
        new_session = SessionPacket().process(packet, None)
        self.assertEqual(new_session.is_online_game, True)
        packet_2 = get_packet_mock()
        packet_2.header.sessionUID = "george2022"
        packet_2.networkGame = 0
        new_session_2 = SessionPacket().process(packet_2, new_session)
        self.assertEqual(new_session_2.is_online_game, False)

    def test_session_weather_changes(self):
        # add first value
        session = Session(session_uid="vettel2021")
        packet = get_packet_mock()
        packet.sessionType = 10
        packet.trackId = 5
        packet.weather = 1
        session = SessionPacket().process(packet, session)
        self.assertEqual(session.weather_ids, [1])
        # add a new value
        packet = get_packet_mock()
        packet.sessionType = 10
        packet.trackId = 5
        packet.weather = 4
        session = SessionPacket().process(packet, session)
        self.assertEqual(session.weather_ids, [1, 4])
        # add the same value again
        packet = get_packet_mock()
        packet.sessionType = 10
        packet.trackId = 5
        packet.weather = 4
        session = SessionPacket().process(packet, session)
        self.assertEqual(session.weather_ids, [1, 4])



class LapPacketTest(TestCase):

    def test_lap_none(self):
        session = Session(session_uid="vettel2021")
        packet = get_packet_mock()
        packet.lapData = [MagicMock(currentLapNum=1, currentLapTime=1, sector1TimeInMS=1000, sector2TimeInMS=0, pitStatus=0, carPosition=1)]
        session = LapPacket().process(packet, session)
        self.assertEqual(session.lap_list, {1: {'sector_1_time_ms': 1000, 'sector_2_time_ms': 0, 'sector_3_time_ms': 0, 'lap_number': 1, 'car_race_position': 1, 'pit_status': 0, 'is_valid': True}})
        self.assertEqual(session.lap_number_current, 1)


    def test_lap_current(self):
        session = Session(session_uid="vettel2021")        
        session.lap_number_current = 2
        session.lap_list = { 2: {"sector_1_time_ms" : 10002, "sector_2_time_ms": 20002, "sector_3_time_ms": 30002, "lap_number": 2, "car_race_position": 1, "pit_status": 1}}
        packet = get_packet_mock()
        packet.lapData = [MagicMock(currentLapNum=2, currentLapTime=80, sector1TimeInMS=10002, sector2TimeInMS=20002, pitStatus=2, carPosition=4, currentLapInvalid=0)]
        session = LapPacket().process(packet, session)
        self.assertEqual(session.lap_list, {2: {'sector_1_time_ms': 10002, 'sector_2_time_ms': 20002, 'sector_3_time_ms': 49996, 'lap_number': 2, 'car_race_position': 4, 'pit_status': 2, 'is_valid': True}})
        self.assertEqual(session.lap_number_current, 2)
        # invalid lap
        packet.lapData = [MagicMock(currentLapNum=2, currentLapTime=80, sector1TimeInMS=10002, sector2TimeInMS=20002, pitStatus=2, carPosition=4, currentLapInvalid=1)]
        session = LapPacket().process(packet, session)
        self.assertEqual(session.lap_list, {2: {'sector_1_time_ms': 10002, 'sector_2_time_ms': 20002, 'sector_3_time_ms': 49996, 'lap_number': 2, 'car_race_position': 4, 'pit_status': 2, 'is_valid': False}})

    def test_lap_new_without_old(self):
        session = Session(session_uid="vettel2021")        
        session.lap_number_current = 1
        packet = get_packet_mock()
        packet.lapData = [MagicMock(currentLapNum=2, currentLapTime=80, sector1TimeInMS=10002, sector2TimeInMS=20002, pitStatus=2, carPosition=4, lastLapTime=60.006)]
        session = LapPacket().process(packet, session)
        self.assertEqual(session.lap_list, {
                    2: {'sector_1_time_ms': 10002, 'sector_2_time_ms': 20002, 'sector_3_time_ms': 49996, 'lap_number': 2, 'car_race_position': 4, 'pit_status': 2, 'is_valid': True}
                    })
        self.assertEqual(session.lap_number_current, 2)

    def test_lap_new_with_old(self):
        session = Session(session_uid="vettel2021")        
        session.lap_number_current = 1
        session.lap_list = { 1: {"sector_1_time_ms" : 10002, "sector_2_time_ms": 20002, "sector_3_time_ms": 30002, "lap_number": 1, "car_race_position": 1, "pit_status": 1, 'is_valid': True}}
        session.process_lap_in_f1laps = MagicMock()
        packet = get_packet_mock()
        packet.lapData = [MagicMock(currentLapNum=2, currentLapTime=80, sector1TimeInMS=10002, sector2TimeInMS=20002, pitStatus=2, carPosition=4, lastLapTime=60.006)]
        session = LapPacket().process(packet, session)
        self.assertEqual(session.lap_list, {
                    1: {"sector_1_time_ms" : 10002, "sector_2_time_ms": 20002, "sector_3_time_ms": 30002, "lap_number": 1, "car_race_position": 1, "pit_status": 1, 'is_valid': True},
                    2: {'sector_1_time_ms': 10002, 'sector_2_time_ms': 20002, 'sector_3_time_ms': 49996, 'lap_number': 2, 'car_race_position': 4, 'pit_status': 2, 'is_valid': True}
                    })
        self.assertEqual(session.lap_number_current, 2)
        session.process_lap_in_f1laps.assert_called_with(1)

    def test_lap_new_with_old_without_sector_2(self):
        session = Session(session_uid="vettel2021")
        session.lap_number_current = 1
        session.lap_list = { 1: {"sector_1_time_ms" : 0, "sector_2_time_ms": 0, "sector_3_time_ms": 30002, "lap_number": 1, "car_race_position": 1, "pit_status": 1, 'is_valid': True}}
        session.process_lap_in_f1laps = MagicMock()
        packet = get_packet_mock()
        packet.lapData = [MagicMock(currentLapNum=2, currentLapTime=80, sector1TimeInMS=10002, sector2TimeInMS=20002, pitStatus=2, carPosition=4, lastLapTime=30.002)]
        session = LapPacket().process(packet, session)
        self.assertEqual(session.lap_list, {
                    1: {"sector_1_time_ms" : 0, "sector_2_time_ms": 0, "sector_3_time_ms": 30002, "lap_number": 1, "car_race_position": 1, "pit_status": 1, 'is_valid': True},
                    2: {'sector_1_time_ms': 10002, 'sector_2_time_ms': 20002, 'sector_3_time_ms': 49996, 'lap_number': 2, 'car_race_position': 4, 'pit_status': 2, 'is_valid': True}
                    })
        self.assertEqual(session.lap_number_current, 2)
        session.process_lap_in_f1laps.assert_not_called()


class CarStatusPacketTest(TestCase):

    def test_process_successful(self):
        session = Session(session_uid="vettel2021")
        session.lap_number_current = 1
        session.lap_list = { 1: {"sector_1_time_ms" : 0, "sector_2_time_ms": 0, "sector_3_time_ms": 30002, "lap_number": 1, "car_race_position": 1, "pit_status": 1, 'is_valid': True}}
        packet = get_packet_mock()
        packet.carStatusData = [MagicMock(visualTyreCompound=7)]
        session = CarStatusPacket().process(packet, session)
        self.assertEqual(session.lap_list[session.lap_number_current]["tyre_compound_visual"], 7)

    def test_process_no_current_lap(self):
        session = Session(session_uid="vettel2021")
        packet = get_packet_mock()
        packet.carStatusData = [MagicMock(visualTyreCompound=7)]
        session = CarStatusPacket().process(packet, session)
        self.assertEqual(session.lap_list, {})

    def test_process_no_lap_list(self):
        session = Session(session_uid="vettel2021")
        session.lap_number_current = 1
        packet = get_packet_mock()
        packet.carStatusData = [MagicMock(visualTyreCompound=7)]
        session = CarStatusPacket().process(packet, session)
        self.assertEqual(session.lap_list, {})

    def test_process_no_lap_list_with_current_lap(self):
        session = Session(session_uid="vettel2021")
        session.lap_number_current = 1
        session.lap_list = { 0: {"sector_1_time_ms" : 0, "sector_2_time_ms": 0, "sector_3_time_ms": 30002, "lap_number": 1, "car_race_position": 1, "pit_status": 1, 'is_valid': True}}
        packet = get_packet_mock()
        packet.carStatusData = [MagicMock(visualTyreCompound=7)]
        session = CarStatusPacket().process(packet, session)
        self.assertEqual(session.lap_list.get(session.lap_number_current), None)


class FinalClassificationPacketTest(TestCase):

    def test_process(self):
        session = Session(session_uid="vettel2021")
        session.process_lap_in_f1laps = MagicMock()
        packet = get_packet_mock()
        packet.classificationData = [MagicMock(position=2, resultStatus=3, points=21)]
        session = FinalClassificationPacket().process(packet, session)
        self.assertEqual(session.finish_position, 2)
        self.assertEqual(session.result_status, 3)
        self.assertEqual(session.points, 21)
        session.process_lap_in_f1laps.assert_called_with()



if __name__ == '__main__':
    unittest.main()