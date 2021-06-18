from unittest import TestCase
from unittest.mock import MagicMock, patch
import json

from receiver.f12020.api import F1LapsAPI
import config


class F1LapsAPITest(TestCase):

    @patch('platform.release')
    @patch('platform.system')
    def test_get_headers(self, mock_system, mock_release):
        mock_system.return_value = "F1Laps Test Runner"
        mock_release.return_value = "2021.02.28"
        headers = F1LapsAPI("vettel4tw", "f12020")._get_headers()
        self.assertEqual(headers, {
            'Content-Type'      : 'application/json',
            'Authorization'     : 'Token vettel4tw',
            'X-F1Laps-App'      : 'F1Laps Telemetry v%s' % config.VERSION,
            'X-F1Laps-Platform' : "F1Laps Test Runner 2021.02.28"
            })

    @patch('receiver.f12020.api.F1LapsAPI.session_create')
    @patch('receiver.f12020.api.F1LapsAPI.session_update')
    @patch('receiver.f12020.api.F1LapsAPI.session_list')
    def test_session_create_or_update_successful_create(self, mock_session_list, mock_session_update, mock_session_create):
        mock_session_create.return_value = MagicMock(status_code=201, content=json.dumps({'id': 'vettel2021'}))
        api = F1LapsAPI("vettel4tw", "f12020")
        success, f1laps_session_id = api.session_create_or_update(
            f1laps_session_id = None, track_id = 1, team_id = 2, session_uid = 345, 
            conditions = 'dry', session_type = 'race', finish_position = None, points = None,
            result_status = None, lap_times = [], setup_data = {}, is_online_game = False
        )
        self.assertEqual(success, True)
        self.assertEqual(f1laps_session_id, "vettel2021")
        self.assertEqual(mock_session_create.call_count, 1)
        self.assertEqual(mock_session_update.call_count, 0)
        self.assertEqual(mock_session_list.call_count, 0)

    @patch('receiver.f12020.api.F1LapsAPI.session_create')
    @patch('receiver.f12020.api.F1LapsAPI.session_update')
    @patch('receiver.f12020.api.F1LapsAPI.session_list')
    def test_session_create_or_update_successful_update(self, mock_session_list, mock_session_update, mock_session_create):
        mock_session_update.return_value = MagicMock(status_code=200)
        api = F1LapsAPI("vettel4tw", "f12020")
        success, f1laps_session_id = api.session_create_or_update(
            f1laps_session_id = "vettel2021", track_id = 1, team_id = 2, session_uid = 345, 
            conditions = 'dry', session_type = 'race', finish_position = None, points = None,
            result_status = None, lap_times = [], setup_data = {}, is_online_game = False
        )
        self.assertEqual(success, True)
        self.assertEqual(f1laps_session_id, "vettel2021")
        self.assertEqual(mock_session_create.call_count, 0)
        self.assertEqual(mock_session_update.call_count, 1)
        self.assertEqual(mock_session_list.call_count, 0)

    @patch('receiver.f12020.api.F1LapsAPI.session_create')
    @patch('receiver.f12020.api.F1LapsAPI.session_update')
    @patch('receiver.f12020.api.F1LapsAPI.session_list')
    def test_session_create_or_update_failed_create_success_update(self, mock_session_list, mock_session_update, mock_session_create):
        mock_session_create.return_value = MagicMock(status_code=400)
        mock_session_list.return_value = MagicMock(status_code=200, content=json.dumps({'results': [{'id': 'vettel2021'}]}))
        mock_session_update.return_value = MagicMock(status_code=200)
        api = F1LapsAPI("vettel4tw", "f12020")
        success, f1laps_session_id = api.session_create_or_update(
            f1laps_session_id = None, track_id = 1, team_id = 2, session_uid = 345, 
            conditions = 'dry', session_type = 'race', finish_position = None, points = None,
            result_status = None, lap_times = [], setup_data = {}, is_online_game = False
        )
        self.assertEqual(success, True)
        self.assertEqual(f1laps_session_id, "vettel2021")
        self.assertEqual(mock_session_create.call_count, 1)
        self.assertEqual(mock_session_update.call_count, 1)
        self.assertEqual(mock_session_list.call_count, 1)

    @patch('receiver.f12020.api.F1LapsAPI.session_create')
    @patch('receiver.f12020.api.F1LapsAPI.session_update')
    @patch('receiver.f12020.api.F1LapsAPI.session_list')
    def test_session_create_or_update_failed_create_failed_list(self, mock_session_list, mock_session_update, mock_session_create):
        mock_session_create.return_value = MagicMock(status_code=400)
        mock_session_list.return_value = MagicMock(status_code=200, content=json.dumps({'results': []}))
        api = F1LapsAPI("vettel4tw", "f12020")
        success, f1laps_session_id = api.session_create_or_update(
            f1laps_session_id = None, track_id = 1, team_id = 2, session_uid = 345, 
            conditions = 'dry', session_type = 'race', finish_position = None, points = None,
            result_status = None, lap_times = [], setup_data = {}, is_online_game = False
        )
        self.assertEqual(success, False)
        self.assertEqual(f1laps_session_id, None)
        self.assertEqual(mock_session_create.call_count, 1)
        self.assertEqual(mock_session_update.call_count, 0)
        self.assertEqual(mock_session_list.call_count, 1)

    @patch('receiver.f12020.api.F1LapsAPI.session_create')
    @patch('receiver.f12020.api.F1LapsAPI.session_update')
    @patch('receiver.f12020.api.F1LapsAPI.session_list')
    def test_session_create_or_update_failed_create(self, mock_session_list, mock_session_update, mock_session_create):
        mock_session_create.return_value = MagicMock(status_code=500, content=json.dumps('fail'))
        api = F1LapsAPI("vettel4tw", "f12020")
        success, f1laps_session_id = api.session_create_or_update(
            f1laps_session_id = None, track_id = 1, team_id = 2, session_uid = 345, 
            conditions = 'dry', session_type = 'race', finish_position = None, points = None,
            result_status = None, lap_times = [], setup_data = {}, is_online_game = False
        )
        self.assertEqual(success, False)
        self.assertEqual(f1laps_session_id, None)
        self.assertEqual(mock_session_create.call_count, 1)
        self.assertEqual(mock_session_update.call_count, 0)
        self.assertEqual(mock_session_list.call_count, 0)

    @patch('receiver.f12020.api.F1LapsAPI.session_create')
    @patch('receiver.f12020.api.F1LapsAPI.session_update')
    @patch('receiver.f12020.api.F1LapsAPI.session_list')
    def test_session_create_or_update_failed_update(self, mock_session_list, mock_session_update, mock_session_create):
        mock_session_update.return_value = MagicMock(status_code=500, content=json.dumps('fail'))
        api = F1LapsAPI("vettel4tw", "f12020")
        success, f1laps_session_id = api.session_create_or_update(
            f1laps_session_id = "vettel2021", track_id = 1, team_id = 2, session_uid = 345, 
            conditions = 'dry', session_type = 'race', finish_position = None, points = None,
            result_status = None, lap_times = [], setup_data = {}, is_online_game = False
        )
        self.assertEqual(success, False)
        self.assertEqual(f1laps_session_id, "vettel2021")
        self.assertEqual(mock_session_create.call_count, 0)
        self.assertEqual(mock_session_update.call_count, 1)
        self.assertEqual(mock_session_list.call_count, 0)


if __name__ == '__main__':
    unittest.main()