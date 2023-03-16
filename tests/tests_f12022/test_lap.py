from unittest import TestCase

from receiver.f12022.lap import F12022Lap
from receiver.f12022.penalty import F12022Penalty


class F12022LapTest(TestCase):
    def test_create(self):
        lap = F12022Lap(lap_number=2, session_type=11, telemetry_enabled=True)
        self.assertEqual(lap.lap_number, 2)
        self.assertFalse(lap.is_in_or_outlap(500, None))
        
    def test_is_in_or_outlap(self):
        # Set session type to one with outlaps (11 = race)
        lap = F12022Lap(lap_number=2, session_type=11, telemetry_enabled=True)
        lap.sector_1_ms = 1
        lap.sector_2_ms = 2
        lap.sector_3_ms = 3
        # All sectors set and < 200 is inlap
        self.assertTrue(lap.is_in_or_outlap(100, 0))
        self.assertTrue(lap.is_race_inlap(100))
        # All sectors set and > 200 is not outlap
        self.assertFalse(lap.is_in_or_outlap(300, 0))
        self.assertFalse(lap.is_race_inlap(300))
        # Not all sectors set is never inlap
        lap.sector_1_ms = 1
        lap.sector_2_ms = 2
        lap.sector_3_ms = None
        self.assertFalse(lap.is_race_inlap(100))
        self.assertFalse(lap.is_race_inlap(100))
    
    def test_is_quali_out_or_inlap(self):
        # Set session type to one with in/outlaps (5 = Q1)
        lap = F12022Lap(lap_number=2, session_type=5, telemetry_enabled=True)
        # No pit status is not an in/outlap
        self.assertFalse(lap.is_in_or_outlap(500, None))
        self.assertFalse(lap.is_quali_out_or_inlap(None))
        # Pit status = 0 is not an in/outlap
        self.assertFalse(lap.is_in_or_outlap(500, 0))
        self.assertFalse(lap.is_quali_out_or_inlap(0))
        # Pit status = 1 is an in/outlap
        self.assertTrue(lap.is_in_or_outlap(500, 1))
        self.assertTrue(lap.is_quali_out_or_inlap(1))
    
    def test_set_pit_status(self):
        lap = F12022Lap(lap_number=2, session_type=11, telemetry_enabled=True)
        self.assertEqual(lap.set_pit_status(1), 1)
        self.assertEqual(lap.pit_status, 1)
        self.assertEqual(lap.set_pit_status(3), 3)
        self.assertEqual(lap.pit_status, 3)
        self.assertEqual(lap.set_pit_status(2), 3)
        self.assertEqual(lap.pit_status, 3)
    
    def test_new_lap_data_should_be_writte(self):
        # Test time trial first
        lap = F12022Lap(lap_number=2, session_type=13, telemetry_enabled=True)
        # Set values so that they should be true except for TT
        lap.sector_1_ms = 1
        lap.sector_2_ms = 2
        lap.sector_3_ms = 3
        self.assertTrue(lap.new_lap_data_should_be_written(0, 123))
        self.assertFalse(lap.new_lap_data_should_be_written(0, 0))
        # Set session type to non-time-trial (5 = race)
        lap.session_type = 5
        self.assertFalse(lap.new_lap_data_should_be_written(0, 100))
        # Non-null value should be false
        self.assertTrue(lap.new_lap_data_should_be_written(5, 0))
        # Not all sectors set is never complete
        lap.sector_3_ms = None
        self.assertTrue(lap.new_lap_data_should_be_written(0, 0))
    
    def test_lap_update(self):
        # Start time trial lap (avoids the in/out lap dependencies)
        lap = F12022Lap(lap_number=2, session_type=13, telemetry_enabled=True)
        lap.update(
            lap_values = {
                "sector_1_ms": 100,
                "sector_2_ms": 200,
                "sector_3_ms": 300,
                "pit_status": 1,
                "is_valid": False,
                "car_race_position": 5
            },
            telemetry_values = {
                "lap_distance": 5,
                "frame_identifier": 1000,
                "lap_time": 50,
            }
        )
        self.assertEqual(lap.sector_1_ms, 100)
        self.assertEqual(lap.pit_status, 1)
        self.assertEqual(lap.is_valid, False)
        self.assertEqual(lap.car_race_position, 5)
        self.assertEqual(lap.telemetry.frame_dict, {1000: [5, 50, None, None, None, None, None, None]})
        self.assertEqual(lap.telemetry.lap_number, 2)
        self.assertEqual(lap.telemetry.session_type, 13)
        self.assertEqual(lap.telemetry.last_lap_distance, 5)
        self.assertEqual(lap.telemetry.frames_popped_list, [])
        # Without tyre wear temp store, it should be None
        self.assertEqual(lap.lap_start_tyre_wear_front_left, None)
        # Without laptime tyre wear should be None
        lap.tyre_wear_current_values_temp_store = [1, 2, 3, 4]
        lap.update(telemetry_values = {"lap_time": 0, "frame_identifier": 1001, "lap_distance": 5}, lap_values = {})
        self.assertEqual(lap.lap_start_tyre_wear_front_left, None)
        # With laptime tyre wear should be set
        lap.update(telemetry_values = {"lap_time": 12, "frame_identifier": 1002, "lap_distance": 5}, lap_values = {})
        self.assertEqual(lap.lap_start_tyre_wear_front_left, 1)
        # Assert temp store is cleared
        self.assertEqual(lap.tyre_wear_current_values_temp_store, [])
    
    def test_can_be_synced_to_f1laps(self):
        lap = F12022Lap(lap_number=2, session_type=13, telemetry_enabled=True)
        # No sync without sector times
        self.assertFalse(lap.can_be_synced_to_f1laps())
        # Ready for sync with sector times
        lap.sector_1_ms = 1
        lap.sector_2_ms = 2
        lap.sector_3_ms = 3
        self.assertTrue(lap.can_be_synced_to_f1laps())
        # No more sync when synced previously
        lap.has_been_synced_to_f1l = True
        self.assertFalse(lap.can_be_synced_to_f1laps())
    
    def test_json_serialize_and_telemetry_enabled(self):
        lap = F12022Lap(lap_number=2, session_type=13, telemetry_enabled=True)
        lap.sector_1_ms = 1
        lap.sector_2_ms = 2
        lap.sector_3_ms = 3
        lap.telemetry = lap.telemetry_model(lap.lap_number, lap.session_type)
        lap.telemetry.frame_dict = {1000: [5, 50, None, None, None, None, None, None]}
        self.assertEqual(lap.json_serialize(), {'lap_number': 2, 'sector_1_time_ms': 1, 'sector_2_time_ms': 2, 'sector_3_time_ms': 3, 'pit_status': None, 'car_race_position': None, 'tyre_compound_visual': None, 'air_temperature': None, 'rain_percentage_forecast': None, 'track_temperature': None, 'weather_id': None, "lap_start_tyre_wear_front_left": None, "lap_start_tyre_wear_front_right": None, "lap_start_tyre_wear_rear_left": None, "lap_start_tyre_wear_rear_right": None, "sector_1_tyre_wear_front_left": None, "sector_1_tyre_wear_front_right": None, "sector_1_tyre_wear_rear_left": None, "sector_1_tyre_wear_rear_right": None, "sector_2_tyre_wear_front_left": None, "sector_2_tyre_wear_front_right": None, "sector_2_tyre_wear_rear_left": None, "sector_2_tyre_wear_rear_right": None, "sector_3_tyre_wear_front_left": None, "sector_3_tyre_wear_front_right": None, "sector_3_tyre_wear_rear_left": None, "sector_3_tyre_wear_rear_right": None, "lap_start_ers_store_kj": None,"sector_1_ers_store_kj": None,"sector_2_ers_store_kj": None,"sector_3_ers_store_kj": None, "lap_start_fuel_remaining_kg": None, "sector_1_fuel_remaining_kg": None, "sector_2_fuel_remaining_kg": None, "sector_3_fuel_remaining_kg": None, "top_speed": 0, "number_gear_changes": 0, "tyre_front_left_temp_max_surface": 0, "tyre_front_right_temp_max_surface": 0, "tyre_rear_left_temp_max_surface": 0, "tyre_rear_right_temp_max_surface": 0, "tyre_front_left_temp_max_inner": 0, "tyre_front_right_temp_max_inner": 0, "tyre_rear_left_temp_max_inner": 0, "tyre_rear_right_temp_max_inner": 0, 'penalties': [], 'telemetry_data_string': '{"1000": [5, 50, null, null, null, null, null, null]}'})
        # Test without telemetry
        lap.telemetry_enabled = False
        self.assertEqual(lap.json_serialize(), {'lap_number': 2, 'sector_1_time_ms': 1, 'sector_2_time_ms': 2, 'sector_3_time_ms': 3, 'pit_status': None, 'car_race_position': None, 'tyre_compound_visual': None, 'air_temperature': None, 'rain_percentage_forecast': None, 'track_temperature': None, 'weather_id': None, "lap_start_tyre_wear_front_left": None, "lap_start_tyre_wear_front_right": None, "lap_start_tyre_wear_rear_left": None, "lap_start_tyre_wear_rear_right": None, "sector_1_tyre_wear_front_left": None, "sector_1_tyre_wear_front_left": None, "sector_1_tyre_wear_front_right": None, "sector_1_tyre_wear_rear_left": None, "sector_1_tyre_wear_rear_right": None, "sector_2_tyre_wear_front_left": None, "sector_2_tyre_wear_front_right": None, "sector_2_tyre_wear_rear_left": None, "sector_2_tyre_wear_rear_right": None, "sector_3_tyre_wear_front_left": None, "sector_3_tyre_wear_front_right": None, "sector_3_tyre_wear_rear_left": None, "sector_3_tyre_wear_rear_right": None, "lap_start_ers_store_kj": None,"sector_1_ers_store_kj": None,"sector_2_ers_store_kj": None,"sector_3_ers_store_kj": None, "lap_start_fuel_remaining_kg": None, "sector_1_fuel_remaining_kg": None, "sector_2_fuel_remaining_kg": None, "sector_3_fuel_remaining_kg": None, "top_speed": 0, "number_gear_changes": 0, "tyre_front_left_temp_max_surface": 0, "tyre_front_right_temp_max_surface": 0, "tyre_rear_left_temp_max_surface": 0, "tyre_rear_right_temp_max_surface": 0, "tyre_front_left_temp_max_inner": 0, "tyre_front_right_temp_max_inner": 0, "tyre_rear_left_temp_max_inner": 0, "tyre_rear_right_temp_max_inner": 0, 'penalties': [], 'telemetry_data_string': None})
        # Test with penalty
        penalty = F12022Penalty()
        penalty.penalty_type = 1
        lap.penalties = [penalty]
        self.assertEqual(lap.json_serialize(), {'lap_number': 2, 'sector_1_time_ms': 1, 'sector_2_time_ms': 2, 'sector_3_time_ms': 3, 'pit_status': None, 'car_race_position': None, 'tyre_compound_visual': None, 'air_temperature': None, 'rain_percentage_forecast': None, 'track_temperature': None, 'weather_id': None, "lap_start_tyre_wear_front_left": None, "lap_start_tyre_wear_front_right": None, "lap_start_tyre_wear_rear_left": None, "lap_start_tyre_wear_rear_right": None, "sector_1_tyre_wear_front_left": None, "sector_1_tyre_wear_front_left": None, "sector_1_tyre_wear_front_right": None, "sector_1_tyre_wear_rear_left": None, "sector_1_tyre_wear_rear_right": None, "sector_2_tyre_wear_front_left": None, "sector_2_tyre_wear_front_right": None, "sector_2_tyre_wear_rear_left": None, "sector_2_tyre_wear_rear_right": None, "sector_3_tyre_wear_front_left": None, "sector_3_tyre_wear_front_right": None, "sector_3_tyre_wear_rear_left": None, "sector_3_tyre_wear_rear_right": None,"lap_start_ers_store_kj": None,"sector_1_ers_store_kj": None,"sector_2_ers_store_kj": None,"sector_3_ers_store_kj": None, "lap_start_fuel_remaining_kg": None, "sector_1_fuel_remaining_kg": None, "sector_2_fuel_remaining_kg": None, "sector_3_fuel_remaining_kg": None, "top_speed": 0, "number_gear_changes": 0, "tyre_front_left_temp_max_surface": 0, "tyre_front_right_temp_max_surface": 0, "tyre_rear_left_temp_max_surface": 0, "tyre_rear_right_temp_max_surface": 0, "tyre_front_left_temp_max_inner": 0, "tyre_front_right_temp_max_inner": 0, "tyre_rear_left_temp_max_inner": 0, "tyre_rear_right_temp_max_inner": 0, 'penalties': [{'frame_id': penalty.frame_id, 'infringement_type': None, 'lap_number': None, 'other_vehicle_index': None, 'penalty_type': 1, 'places_gained': None, 'time_spent_gained': None, 'vehicle_index': None}], 'telemetry_data_string': None})

    def test_process_flashback_event_removes_penalties(self):
        lap = F12022Lap(lap_number=2, session_type=13, telemetry_enabled=True)
        penalty = F12022Penalty()
        penalty.penalty_type = 1
        penalty.frame_id = 1001
        penalty_2 = F12022Penalty()
        penalty_2.penalty_type = 1
        penalty_2.frame_id = 1003
        lap.penalties = [penalty, penalty_2]
        lap.process_flashback_event(1002)
        self.assertEqual(lap.penalties, [penalty])
    
    def test_store_tyre_wear(self):
        lap = F12022Lap(lap_number=2, session_type=13, telemetry_enabled=True)
        # Make sure 0 values don't count
        lap.store_tyre_wear(0, 0, 0, 0)
        self.assertEqual(lap.lap_start_tyre_wear_rear_right, None)
        self.assertEqual(lap.sector_1_tyre_wear_front_right, None)
        # No sector times (means we're in S1)
        lap.store_tyre_wear(1, 2, 3, 0.0001)
        self.assertEqual(lap.lap_start_tyre_wear_rear_right, 0.0001)
        self.assertEqual(lap.sector_1_tyre_wear_front_right, 2)
        self.assertEqual(lap.sector_2_tyre_wear_front_right, None)
        self.assertEqual(lap.sector_3_tyre_wear_front_right, None)
        # Start S2
        lap.sector_1_ms = 100
        lap.store_tyre_wear(2, 4, 6, 8)
        self.assertEqual(lap.lap_start_tyre_wear_rear_right, 0.0001)
        self.assertEqual(lap.sector_1_tyre_wear_front_right, 2)
        self.assertEqual(lap.sector_2_tyre_wear_front_right, 4)
        self.assertEqual(lap.sector_3_tyre_wear_front_right, None)
        # Start S3
        lap.sector_2_ms = 100
        lap.sector_3_ms = 100
        lap.store_tyre_wear(4, 8, 12, 16)
        self.assertEqual(lap.lap_start_tyre_wear_rear_right, 0.0001)
        self.assertEqual(lap.sector_1_tyre_wear_front_right, 2)
        self.assertEqual(lap.sector_2_tyre_wear_front_right, 4)
        self.assertEqual(lap.sector_3_tyre_wear_front_right, 8)
    
    def test_store_top_speed_gear_max_tyre_wear(self):
        lap = F12022Lap(lap_number=2, session_type=13, telemetry_enabled=True)
        lap.update_max_speed_max_temp_gear_changes({'speed': 50, "gear": 2, "tyre_front_right_temp_max_surface": 50, "tyre_rear_left_temp_max_inner": 10})
        self.assertEqual(lap.top_speed, 50)
        self.assertEqual(lap.number_gear_changes, 1)
        self.assertEqual(lap.tyre_front_right_temp_max_surface, 50)
        self.assertEqual(lap.tyre_rear_left_temp_max_inner, 10)
        # Lower values
        lap.update_max_speed_max_temp_gear_changes({'speed': 30, "gear": 1, "tyre_front_right_temp_max_surface": 40, "tyre_rear_left_temp_max_inner": 9})
        self.assertEqual(lap.top_speed, 50)
        self.assertEqual(lap.number_gear_changes, 2)
        self.assertEqual(lap.tyre_front_right_temp_max_surface, 50)
        self.assertEqual(lap.tyre_rear_left_temp_max_inner, 10)
        # Higher values
        lap.update_max_speed_max_temp_gear_changes({'speed': 60, "gear": 1, "tyre_front_right_temp_max_surface": 60, "tyre_rear_left_temp_max_inner": 11})
        self.assertEqual(lap.top_speed, 60)
        self.assertEqual(lap.number_gear_changes, 2)
        self.assertEqual(lap.tyre_front_right_temp_max_surface, 60)
        self.assertEqual(lap.tyre_rear_left_temp_max_inner, 11)


if __name__ == '__main__':
    unittest.main()