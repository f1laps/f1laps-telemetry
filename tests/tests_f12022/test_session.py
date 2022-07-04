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
        session.update_weather(2)
        self.assertEqual(session.weather_ids, {1, 2})
        session.update_weather(1)
        self.assertEqual(session.weather_ids, {1, 2})
    
    def test_get_lap(self):
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        lap = session.get_lap(1)
        self.assertEqual(lap.lap_number, 1)
    
    def test_can_be_synced_to_f1laps(self):
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        # No team ID
        self.assertFalse(session.can_be_synced_to_f1laps())
        # With team ID
        session.team_id = 0
        self.assertTrue(session.can_be_synced_to_f1laps())
    
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
        mock_session_sync.assert_called_once_with(f1laps_session_id=None, track_id=1, team_id=1, session_uid='uid_123', conditions='dry', session_type='race', game_mode='time_trial', finish_position=None, points=None, result_status=None, lap_times=[{'lap_number': 1, 'sector_1_time_ms': 1, 'sector_2_time_ms': 2, 'sector_3_time_ms': 3, 'car_race_position': None, 'pit_status': None, 'tyre_compound_visual': None, 'telemetry_data_string': None}], setup_data={}, is_online_game=False, ai_difficulty=90, classifications=[])        
        self.assertEqual(mock_lap_sync.call_count, 0)
        self.assertFalse(lap.has_been_synced_to_f1l)
        # Second test time trial session (syncs single lap)
        session.session_type = 13
        session.sync_to_f1laps(1)
        self.assertEqual(mock_session_sync.call_count, 1)
        self.assertEqual(mock_lap_sync.call_count, 1)
        self.assertTrue(lap.has_been_synced_to_f1l)
        mock_lap_sync.assert_called_once_with(track_id=1, team_id=1, conditions='dry', game_mode='time_trial', sector_1_time=1, sector_2_time=2, sector_3_time=3, setup_data={}, is_valid=True, telemetry_data_string=None)        
        # Third test sync_entire_session flag
        # Needs race session type
        session.session_type = 10
        session.sync_to_f1laps(lap_number=None, sync_entire_session=True)
        self.assertEqual(mock_session_sync.call_count, 2)
        self.assertEqual(mock_lap_sync.call_count, 1)
    
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

        


if __name__ == '__main__':
    unittest.main()