from unittest import TestCase
from unittest.mock import patch

from receiver.f12022.session import F12022Session


class F12022SessionTest(TestCase):
    def test_create(self):
        session = F12022Session(
            "f1laps_key_123",
            True, # with telemetry
            "uid_123",
            10, # session type = race
            1, # track id
            False, # offline
            90, # ai difficulty
            1, # weather
            5 # game mode
        )
        self.assertEqual(session.session_udp_uid, "uid_123")
        self.assertEqual(session.game_version, "f12022")
        self.assertEqual(session.get_session_type(), "race")
        self.assertEqual(session.game_mode, "time_trial")
    
    def test_update_weather(self):
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        self.assertEqual(session.weather_ids, {1})
        session.update_weather(2, 10, 30, 0.5)
        self.assertEqual(session.weather_ids, {1, 2})
        # Test with lap
        lap = session.add_lap(1)
        self.assertEqual(lap.weather_id, None)
        self.assertEqual(lap.air_temperature, None)
        self.assertEqual(lap.rain_percentage_forecast, None)
        session.update_weather(1, 10, 20, 0.0)
        self.assertEqual(session.weather_ids, {1, 2})
        self.assertEqual(lap.weather_id, 1)
        self.assertEqual(lap.air_temperature, 20)
        self.assertEqual(lap.rain_percentage_forecast, 0.0)
    
    def test_get_lap(self):
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        lap = session.get_lap(1)
        self.assertEqual(lap.lap_number, 1)
    
    def test_is_valid_for_f1laps(self):
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        # No team ID
        self.assertFalse(session.is_valid_for_f1laps())
        # With team ID
        session.team_id = 2
        self.assertTrue(session.is_valid_for_f1laps())
        # With team ID of 0 (Mercedes)
        session.team_id = 0
        self.assertTrue(session.is_valid_for_f1laps())
    
    def test_is_multi_lap_session(self):
        # Session type 10 = race 
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        self.assertTrue(session.is_multi_lap_session())
        # Session type 13 = time trial
        session = F12022Session("key_123", True, "uid_123", 13, 1, False, 90, 1, 5)
        self.assertFalse(session.is_multi_lap_session())
    
    def test_get_current_lap(self):
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        self.assertEqual(session.get_current_lap(), None)
        lap = session.add_lap(1)
        self.assertEqual(session.get_current_lap(), lap)
        lap_2 = session.add_lap(2)
        self.assertEqual(session.get_current_lap(), lap_2)
    
    @patch('receiver.f12022.session.F1LapsAPI2022.session_create_or_update')
    @patch('receiver.f12022.session.F1LapsAPI2022.lap_create')
    def test_sync_to_f1laps(self, mock_lap_sync, mock_session_sync):
        # Set up mock return values
        mock_session_sync.return_value = True, "123"
        mock_lap_sync.return_value = True
        # First test race session (syncs entire session)
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        session.team_id = 1
        lap = session.add_lap(1)
        session.lap_list[1].sector_1_ms = 1
        session.lap_list[1].sector_2_ms = 2
        session.lap_list[1].sector_3_ms = 3
        session.sync_to_f1laps(1)
        self.assertEqual(mock_session_sync.call_count, 1)
        mock_session_sync.assert_called_once_with(f1laps_session_id=None, track_id=1, team_id=1, session_uid='uid_123', conditions='dry', session_type='race', game_mode='time_trial', finish_position=None, points=None, result_status=None, lap_times=[{'lap_number': 1, 'sector_1_time_ms': 1, 'sector_2_time_ms': 2, 'sector_3_time_ms': 3, 'car_race_position': None, 'pit_status': None, 'tyre_compound_visual': None, 'penalties': [], 'telemetry_data_string': None, 'air_temperature': None, 'track_temperature': None, 'rain_percentage_forecast': None, 'weather_id': None, "sector_1_tyre_wear_front_left": None, "sector_1_tyre_wear_front_right": None, "sector_1_tyre_wear_rear_left": None, "sector_1_tyre_wear_rear_right": None, "sector_2_tyre_wear_front_left": None, "sector_2_tyre_wear_front_right": None, "sector_2_tyre_wear_rear_left": None, "sector_2_tyre_wear_rear_right": None, "sector_3_tyre_wear_front_left": None, "sector_3_tyre_wear_front_right": None, "sector_3_tyre_wear_rear_left": None, "sector_3_tyre_wear_rear_right": None,}], setup_data={}, is_online_game=False, ai_difficulty=90, classifications=[], season_identifier=None)        
        self.assertEqual(mock_lap_sync.call_count, 0)
        self.assertFalse(lap.has_been_synced_to_f1l)
        # Second test time trial session (syncs single lap)
        session.session_type = 13
        session.sync_to_f1laps(1)
        self.assertEqual(mock_session_sync.call_count, 1)
        self.assertEqual(mock_lap_sync.call_count, 1)
        self.assertTrue(lap.has_been_synced_to_f1l)
        mock_lap_sync.assert_called_once_with(track_id=1, team_id=1, conditions='dry', game_mode='time_trial', sector_1_time=1, sector_2_time=2, sector_3_time=3, setup_data={}, is_valid=True, telemetry_data_string=None, air_temperature= None, track_temperature= None, rain_percentage_forecast= None, weather_id= None, sector_1_tyre_wear_front_left = None, sector_1_tyre_wear_front_right = None, sector_1_tyre_wear_rear_left = None, sector_1_tyre_wear_rear_right = None, sector_2_tyre_wear_front_left = None, sector_2_tyre_wear_front_right = None, sector_2_tyre_wear_rear_left = None, sector_2_tyre_wear_rear_right = None, sector_3_tyre_wear_front_left = None, sector_3_tyre_wear_front_right = None, sector_3_tyre_wear_rear_left = None, sector_3_tyre_wear_rear_right = None)        
        # Third test sync_entire_session flag
        # Needs race session type
        session.session_type = 10
        session.sync_to_f1laps(lap_number=None, sync_entire_session=True)
        self.assertEqual(mock_session_sync.call_count, 2)
        self.assertEqual(mock_lap_sync.call_count, 1)

    @patch('receiver.f12022.session.F1LapsAPI2022.session_create_or_update')
    @patch('receiver.f12022.session.F1LapsAPI2022.lap_create')
    def test_sync_to_f1laps_doesnt_sync_without_team_id(self, mock_lap_sync, mock_session_sync):
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        session.team_id = None
        lap = session.add_lap(1)
        session.lap_list[1].sector_1_ms = 1
        session.lap_list[1].sector_2_ms = 2
        session.lap_list[1].sector_3_ms = 3
        session.sync_to_f1laps(1)
        self.assertEqual(mock_session_sync.call_count, 0)
        self.assertEqual(mock_lap_sync.call_count, 0)
        self.assertFalse(lap.has_been_synced_to_f1l)
    
    def test_set_team_id_and_game_mode_update(self):
        # Time trial session
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        session.set_team_id(5)
        self.assertEqual(session.team_id, 5)
        self.assertEqual(session.game_mode, "time_trial")
        # Career session with MyTeam car
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 19)
        self.assertEqual(session.game_mode, "career")
        session.set_team_id(255)
        self.assertEqual(session.team_id, 255)
        self.assertEqual(session.game_mode, "my_team")
        # Career session with non-myteam car
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 19)
        self.assertEqual(session.game_mode, "career")
        session.set_team_id(4)
        self.assertEqual(session.team_id, 4)
        self.assertEqual(session.game_mode, "driver_career")
        # Another update doesn't change anything
        session.set_team_id(255)
        self.assertEqual(session.team_id, 4)
        self.assertEqual(session.game_mode, "driver_career")
    
    def test_get_classification_list(self):
        """ 
        Test that we get the right classification list 
        Starting F1 22, we exclude participants without result_status
        So the list should only return the 2 participants with result_status
        """
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        classifications = session.get_classification_list()
        self.assertEqual(classifications, [])
        session.add_participant(dict(name="Player", team=0, driver=255, driver_index=0))
        session.participants[0].result_status = 5
        session.participants[0].position = 20
        session.add_participant(dict(name="No Result Status should get skipped", team=1, driver=2, driver_index=2))
        session.participants[1].position = 6
        session.participants[1].points = 8
        session.participants[1].grid_position = 18
        session.add_participant(dict(name="Mick Schumi", team=1, driver=1, driver_index=3))
        session.participants[2].result_status = 4
        session.participants[2].position = 5
        session.participants[2].points = 10
        session.participants[2].grid_position = 19
        classifications = session.get_classification_list()
        self.assertEqual(classifications, [{'driver': 255, 'driver_index': 0, 'team': 0, 'points': None, 'finish_position': None, 'grid_position': None, 'result_status': 5, 'lap_time_best': None, 'race_time_total': None, 'penalties_time_total': None, 'penalties_number': None}, {'driver': 1, 'driver_index': 3, 'team': 1, 'points': 10, 'finish_position': None, 'grid_position': 19, 'result_status': 4, 'lap_time_best': None, 'race_time_total': None, 'penalties_time_total': None, 'penalties_number': None}])


        


if __name__ == '__main__':
    unittest.main()