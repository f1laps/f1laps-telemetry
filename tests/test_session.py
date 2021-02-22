from unittest import TestCase
from unittest.mock import MagicMock, patch
import json

from f1laps_telemetry_2020.session import Session
from f1laps_telemetry_2020.f1laps import F1LapsAPI


class SessionBaseTests(TestCase):

    def test_empty_session_object(self):
        session = Session(session_uid="vettel2021")
        self.assertEqual(session.session_udp_uid, "vettel2021")

    def test_map_udp_session_id_to_f1laps_token(self):
        session = Session(session_uid="vettel2021")
        self.assertEqual(session.map_udp_session_id_to_f1laps_token(), None)
        self.assertEqual(session.session_type_supported_by_f1laps_as_session(), False)
        session.session_type = 10
        self.assertEqual(session.map_udp_session_id_to_f1laps_token(), "race")
        self.assertEqual(session.session_type_supported_by_f1laps_as_session(), True)
        session.session_type = 12
        self.assertEqual(session.map_udp_session_id_to_f1laps_token(), "time_trial")
        self.assertEqual(session.session_type_supported_by_f1laps_as_session(), False)

    def test_map_weather_ids_to_f1laps_token(self):
        session = Session(session_uid="vettel2021")
        self.assertEqual(session.map_weather_ids_to_f1laps_token(), "dry")
        session.weather_ids = [1]
        self.assertEqual(session.map_weather_ids_to_f1laps_token(), "dry")
        session.weather_ids = [0, 1]
        self.assertEqual(session.map_weather_ids_to_f1laps_token(), "dry")
        session.weather_ids = [3]
        self.assertEqual(session.map_weather_ids_to_f1laps_token(), "wet")
        session.weather_ids = [3, 5]
        self.assertEqual(session.map_weather_ids_to_f1laps_token(), "wet")
        session.weather_ids = [0, 1, 4, 5]
        self.assertEqual(session.map_weather_ids_to_f1laps_token(), "mixed")

    def test_get_f1laps_lap_times_list(self):
        session = Session(session_uid="vettel2021")
        self.assertEqual(session.get_f1laps_lap_times_list(), [])
        session.lap_list = {
            1: {"sector_1_time_ms" : 10001, "sector_2_time_ms": 20001, "sector_3_time_ms": 30001, "lap_number": 1, "car_race_position": 1, "pit_status": 0},
            2: {"sector_1_time_ms" : 10002, "sector_2_time_ms": 20002, "sector_3_time_ms": 30002, "lap_number": 2, "car_race_position": 1, "pit_status": 1, "tyre_compound_visual": 8},
        }
        self.assertEqual(session.get_f1laps_lap_times_list(), [
            {'car_race_position': 1, 'lap_number': 1, 'pit_status': 0, 'sector_1_time_ms': 10001, 'sector_2_time_ms': 20001, 'sector_3_time_ms': 30001, "tyre_compound_visual": None}, 
            {'car_race_position': 1, 'lap_number': 2, 'pit_status': 1, 'sector_1_time_ms': 10002, 'sector_2_time_ms': 20002, 'sector_3_time_ms': 30002, "tyre_compound_visual": 8}
            ])
        # incomplete lap should not be returned
        session.lap_list = {
            1: {"sector_1_time_ms" : 10001, "sector_2_time_ms": 20001, "sector_3_time_ms": 30001, "lap_number": 1, "car_race_position": 1, "pit_status": 0},
            2: {"sector_1_time_ms" : 10002, "sector_2_time_ms": 20002, "sector_3_time_ms": 30002, "lap_number": 2, "car_race_position": 1, "pit_status": 1, "tyre_compound_visual": 16},
            3: {"sector_1_time_ms" : 10002, "sector_2_time_ms": None , "sector_3_time_ms": 30002, "lap_number": 3, "car_race_position": 1, "pit_status": 1},
        }
        self.assertEqual(session.get_f1laps_lap_times_list(), [
            {'car_race_position': 1, 'lap_number': 1, 'pit_status': 0, 'sector_1_time_ms': 10001, 'sector_2_time_ms': 20001, 'sector_3_time_ms': 30001, "tyre_compound_visual": None}, 
            {'car_race_position': 1, 'lap_number': 2, 'pit_status': 1, 'sector_1_time_ms': 10002, 'sector_2_time_ms': 20002, 'sector_3_time_ms': 30002, "tyre_compound_visual": 16}
            ])

    def test_get_track_name(self):
        session = Session(session_uid="vettel2021")
        self.assertEqual(session.get_track_name(), None)
        session.track_id = 11
        self.assertEqual(session.get_track_name(), "Monza")



class SessionAPITests(TestCase):
    def setUp(self):
        self.session = Session(session_uid="vettel2021")
        self.session.team_id = 1
        self.session.track_id = 5
        self.session.lap_number_current = 2
        self.session.lap_list = {1: {"sector_1_time_ms" : 10001, "sector_2_time_ms": 20001, "sector_3_time_ms": 30001, "lap_number": 1, "car_race_position": 1, "pit_status": 0}}

    @patch('f1laps_telemetry_2020.session.F1LapsAPI.lap_create')
    def test_single_lap_success(self, mock_lap_create_api):
        # set session_type to time_trial to test single lap
        self.session.session_type = 12
        mock_lap_create_api.return_value = MagicMock(status_code=201) 
        self.assertEqual(self.session.process_lap_in_f1laps(1), True)

    @patch('f1laps_telemetry_2020.session.F1LapsAPI.lap_create')
    def test_single_lap_fail(self, mock_lap_create_api):
        # set session_type to time_trial to test single lap
        self.session.session_type = 12
        mock_lap_create_api.return_value = MagicMock(status_code=404, content=json.dumps({"error": "it didnt work"}))
        self.assertEqual(self.session.process_lap_in_f1laps(1), False)

    @patch('f1laps_telemetry_2020.session.F1LapsAPI.session_create')
    def test_session_create_success(self, mock_session_create_api):
        # set session_type to race to test session
        self.session.session_type = 10
        # make sure we have no f1laps id in the session yet
        self.session.f1_laps_session_id = None
        mock_session_create_api.return_value = MagicMock(status_code=201, content=json.dumps({"id": "astonmartin4tw"}))
        self.assertEqual(self.session.process_lap_in_f1laps(1), True)
        self.assertEqual(self.session.f1_laps_session_id, "astonmartin4tw")

    @patch('f1laps_telemetry_2020.session.F1LapsAPI.session_update')
    def test_session_update_success(self, mock_session_update_api):
        # set session_type to race to test session
        self.session.session_type = 10
        # make sure we have a f1laps id in the session
        self.session.f1_laps_session_id = "astonmartin4tw"
        mock_session_update_api.return_value = MagicMock(status_code=200)
        self.assertEqual(self.session.process_lap_in_f1laps(1), True)

    @patch('f1laps_telemetry_2020.session.F1LapsAPI.session_update')
    def test_session_update_error(self, mock_session_update_api):
        # set session_type to race to test session
        self.session.session_type = 10
        # make sure we have a f1laps id in the session
        self.session.f1_laps_session_id = "astonmartin4tw"
        mock_session_update_api.return_value = MagicMock(status_code=404, content=json.dumps({"error": "it didnt work"}))
        self.assertEqual(self.session.process_lap_in_f1laps(1), False)

    @patch('f1laps_telemetry_2020.session.F1LapsAPI.session_update')
    @patch('f1laps_telemetry_2020.session.F1LapsAPI.session_list')
    @patch('f1laps_telemetry_2020.session.F1LapsAPI.session_create')
    def test_session_create_error_list_success_update(self, mock_session_create_api, mock_session_list_api, mock_session_update_api):
        # set session_type to race to test session
        self.session.session_type = 10
        # make sure we don't have a f1laps id in the session yet
        self.session.f1_laps_session_id = None
        mock_session_create_api.return_value = MagicMock(status_code=403, content=json.dumps({"error": "already exists"}))
        mock_session_list_api.return_value = MagicMock(status_code=200, content=json.dumps({"results": [{"id": "astonmartin4tw"}]}))
        mock_session_update_api.return_value = MagicMock(status_code=200)
        self.assertEqual(self.session.process_lap_in_f1laps(1), True)
        self.assertEqual(self.session.f1_laps_session_id, "astonmartin4tw")

    @patch('f1laps_telemetry_2020.session.F1LapsAPI.session_list')
    @patch('f1laps_telemetry_2020.session.F1LapsAPI.session_create')
    def test_session_create_error_list_error(self, mock_session_create_api, mock_session_list_api):
        # set session_type to race to test session
        self.session.session_type = 10
        # make sure we don't have a f1laps id in the session yet
        self.session.f1_laps_session_id = None
        mock_session_create_api.return_value = MagicMock(status_code=403, content=json.dumps({"error": "already exists"}))
        mock_session_list_api.return_value = MagicMock(status_code=200, content=json.dumps({"results": []}))
        self.assertEqual(self.session.process_lap_in_f1laps(1), False)

    @patch('f1laps_telemetry_2020.session.F1LapsAPI.session_create')
    def test_session_create_error_400(self, mock_session_create_api):
        # set session_type to race to test session
        self.session.session_type = 10
        # make sure we don't have a f1laps id in the session yet
        self.session.f1_laps_session_id = None
        mock_session_create_api.return_value = MagicMock(status_code=400, content=json.dumps({"error": "already exists"}))
        self.assertEqual(self.session.process_lap_in_f1laps(1), False)
        


if __name__ == '__main__':
    unittest.main()