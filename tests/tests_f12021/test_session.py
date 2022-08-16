from unittest import TestCase
from unittest.mock import patch, MagicMock

from receiver.f12021.session import F12021Session
from receiver.f12021.penalty import F12021Penalty


class F12021SessionTest(TestCase):
    def test_string(self):
        session = F12021Session(123)
        session.team_id = 1
        session.lap_list = {2: []}
        self.assertEqual(str(session), "None   (ID F12021-123, team 1)")
        session.track_id = 2
        self.assertEqual(str(session), "Shanghai   (ID F12021-123, team 1)")
        session.session_type = 6
        self.assertEqual(str(session), "Shanghai  Qualifying 2 (ID F12021-123, team 1)")
        session.game_mode = "Championship"
        self.assertEqual(str(session), "Shanghai Championship Qualifying 2 (ID F12021-123, team 1)")

    def test_get_track_name(self):
        session = F12021Session(123)
        session.track_id = 5
        self.assertEqual(session.get_track_name(), "Monaco")

    def test_get_session_type(self):
        session = F12021Session(123)
        session.session_type = 7
        self.assertEqual(session.get_session_type(), "qualifying_3")

    def test_lap_should_be_sent_to_f1laps(self):
        session = F12021Session(123)
        # Test lap not found
        self.assertEqual(session.lap_should_be_sent_to_f1laps(1), False)
        session.lap_list = {1: {1: {'lap_number': 1, 'sector_1_ms': 11111, 'sector_2_ms': 22222, 'tyre_compound_visual': 16}}}
        # Test lap doesnt have all sectors
        self.assertEqual(session.lap_should_be_sent_to_f1laps(1), False)
        session.lap_list = {1: {'lap_number': 1, 'sector_1_ms': 11111, 'sector_2_ms': 22222, 'sector_3_ms': 33333, 'tyre_compound_visual': 16}}
        # Test success case
        self.assertEqual(session.lap_should_be_sent_to_f1laps(1), True)
        # Test lap was already sent to F1Laps
        self.assertEqual(session.lap_should_be_sent_to_f1laps(1), False)

    def test_lap_should_be_sent_as_session(self):
        session = F12021Session(123)
        self.assertEqual(session.lap_should_be_sent_as_session(), False)
        session.session_type = 10
        self.assertEqual(session.lap_should_be_sent_as_session(), True)
        session.session_type = 13
        self.assertEqual(session.lap_should_be_sent_as_session(), False)

    @patch('receiver.f12021.session.F1LapsAPI2021.lap_create')
    def test_send_lap_to_f1laps(self, mock_api):
        mock_api.return_value = MagicMock(status_code=201)
        session = F12021Session(123)
        session.track_id = 10
        session.team_id = 2
        session.session_type = 13
        session.lap_list = {1: {'lap_number': 1, 'sector_1_ms': 11111, 'sector_2_ms': 22222, 'sector_3_ms': 33333, 'tyre_compound_visual': 16}}
        self.assertEqual(session.send_lap_to_f1laps(1), None)
        mock_api.assert_called_with(track_id=10, team_id=2, conditions='dry', game_mode='time_trial', sector_1_time=11111, sector_2_time=22222, sector_3_time=33333, setup_data={}, is_valid=True, telemetry_data_string=None)

    @patch('receiver.f12021.session.F1LapsAPI2021.session_create_or_update')
    def test_send_session_to_f1laps(self, mock_api):
        mock_api.return_value = True, "vettel2021"
        session = F12021Session(123)
        session.track_id = 10
        session.team_id = 2
        session.session_type = 10
        session.lap_list = {}
        session.send_session_to_f1laps()
        self.assertEqual(session.f1_laps_session_id, "vettel2021")
        mock_api.assert_called_with(f1laps_session_id=None, track_id=10, team_id=2, session_uid=123, conditions='dry', session_type='race', finish_position=None, points=None, result_status=None, lap_times=[], setup_data={}, is_online_game=False, ai_difficulty=None, classifications=[])

    def test_is_valid_for_f1laps_team_zero(self):
        session = F12021Session(123)
        session.team_id = 0
        session.session_type = 1
        self.assertEqual(session.is_valid_for_f1laps(), True)
        session.team_id = None
        self.assertEqual(session.is_valid_for_f1laps(), False)

    def test_has_final_classification(self):
        session = F12021Session(123)
        self.assertEqual(session.has_final_classification(), False)
        # A positive result status on the session itself always is true
        session.result_status = 5
        self.assertEqual(session.has_final_classification(), True)
        session.result_status = None
        # Participants with no result status - false
        session.add_participant(name="Player", team=0, driver=255, driver_index=0)
        self.assertEqual(session.has_final_classification(), False)
        session.participants[0].result_status = 5
        self.assertEqual(session.has_final_classification(), True)
    
    def test_get_f1laps_lap_times_list(self):
        session = F12021Session(123)
        session.telemetry_enabled = False
        # Empty array without laps
        self.assertEqual(session.get_f1laps_lap_times_list(), [])
        # Add lap
        session.lap_list = {1: {'lap_number': 1, 'sector_1_ms': 11111, 'sector_2_ms': 22222, 'sector_3_ms': 33333}}
        self.assertEqual(session.get_f1laps_lap_times_list(), [{'lap_number': 1, 'sector_1_time_ms': 11111, 'sector_2_time_ms': 22222, 'sector_3_time_ms': 33333, 'car_race_position': None, 'pit_status': None, 'tyre_compound_visual': None, 'telemetry_data_string': None, 'penalties': []}])
        # With penalty
        penalty = F12021Penalty()
        penalty.penalty_type = 1
        session.lap_list[1]['penalties'] = [penalty,]
        self.assertEqual(session.get_f1laps_lap_times_list(), [{'lap_number': 1, 'sector_1_time_ms': 11111, 'sector_2_time_ms': 22222, 'sector_3_time_ms': 33333, 'car_race_position': None, 'pit_status': None, 'tyre_compound_visual': None, 'telemetry_data_string': None, 'penalties': [{'frame_id': penalty.frame_id, 'penalty_type': 1, 'infringement_type': None, 'vehicle_index': None, 'other_vehicle_index': None, 'time_spent_gained': None, 'lap_number': None, 'places_gained': None}]}])
        # With telemetry
        session.telemetry_enabled = True
        telemetry = MagicMock()
        telemetry.get_telemetry_api_dict.return_value = "justasamplestring"
        session.telemetry = telemetry
        self.assertEqual(session.get_f1laps_lap_times_list(), [{'lap_number': 1, 'sector_1_time_ms': 11111, 'sector_2_time_ms': 22222, 'sector_3_time_ms': 33333, 'car_race_position': None, 'pit_status': None, 'tyre_compound_visual': None, 'telemetry_data_string': '"justasamplestring"', 'penalties': [{'frame_id': penalty.frame_id, 'penalty_type': 1, 'infringement_type': None, 'vehicle_index': None, 'other_vehicle_index': None, 'time_spent_gained': None, 'lap_number': None, 'places_gained': None}]}])   

    def test_get_classification_list(self):
        """ 
        Test that we get the right classification list 
        Starting F1 22, we exclude participants without result_status
        This tests F1 2021, so we should get all 3 participants
        """
        session = F12021Session(123)
        classifications = session.get_classification_list()
        self.assertEqual(classifications, [])
        session.add_participant(name="Player", team=0, driver=255, driver_index=0)
        session.participants[0].result_status = 5
        session.participants[0].position = 20
        session.add_participant(name="No Result Status should get skipped", team=1, driver=2, driver_index=2)
        session.participants[1].position = 6
        session.participants[1].points = 8
        session.participants[1].grid_position = 18
        session.add_participant(name="Mick Schumi", team=1, driver=1, driver_index=3)
        session.participants[2].result_status = 4
        session.participants[2].position = 5
        session.participants[2].points = 10
        session.participants[2].grid_position = 19
        classifications = session.get_classification_list()
        self.assertEqual(classifications, [{'driver': 255, 'driver_index': 0, 'team': 0, 'result_status': 5, 'points': None, 'finish_position': None, 'grid_position': None, 'lap_time_best': None, 'race_time_total': None, 'penalties_time_total': None, 'penalties_number': None}, {'driver': 2, 'driver_index': 2, 'team': 1, 'result_status': None, 'points': 8, 'finish_position': None, 'grid_position': 18, 'lap_time_best': None, 'race_time_total': None, 'penalties_time_total': None, 'penalties_number': None}, {'driver': 1, 'driver_index': 3, 'team': 1, 'result_status': 4, 'points': 10, 'finish_position': None, 'grid_position': 19, 'lap_time_best': None, 'race_time_total': None, 'penalties_time_total': None, 'penalties_number': None}])

        


if __name__ == '__main__':
    unittest.main()