from unittest import TestCase

from receiver.f12022.lap import F12022Lap


class F12022SessionTest(TestCase):
    def test_create(self):
        lap = F12022Lap(lap_number=2, session_type=11)
        self.assertEqual(lap.lap_number, 2)
        self.assertFalse(lap.is_in_or_outlap(500))
        
    def test_is_in_or_outlap(self):
        # Set session type to one with outlaps (11 = race)
        lap = F12022Lap(lap_number=2, session_type=11)
        lap.sector_1_ms = 1
        lap.sector_2_ms = 2
        lap.sector_3_ms = 3
        # All sectors set and < 200 is inlap
        self.assertTrue(lap.is_in_or_outlap(100))
        self.assertTrue(lap.is_race_inlap(100))
        # All sectors set and > 200 is not outlap
        self.assertFalse(lap.is_in_or_outlap(300))
        self.assertFalse(lap.is_race_inlap(300))
        # Not all sectors set is never inlap
        lap.sector_1_ms = 1
        lap.sector_2_ms = 2
        lap.sector_3_ms = None
        self.assertFalse(lap.is_race_inlap(100))
        self.assertFalse(lap.is_race_inlap(100))
    
    def test_is_quali_out_or_inlap(self):
        # Set session type to one with in/outlaps (5 = Q1)
        lap = F12022Lap(lap_number=2, session_type=5)
        # No pit status is not an in/outlap
        self.assertFalse(lap.is_in_or_outlap(500))
        self.assertFalse(lap.is_quali_out_or_inlap())
        # Pit status = 0 is not an in/outlap
        lap.pit_status = 0
        self.assertFalse(lap.is_in_or_outlap(500))
        self.assertFalse(lap.is_quali_out_or_inlap())
        # Pit status = 1 is an in/outlap
        lap.pit_status = 1
        self.assertTrue(lap.is_in_or_outlap(500))
        self.assertTrue(lap.is_quali_out_or_inlap())
    
    def test_set_pit_status(self):
        lap = F12022Lap(lap_number=2, session_type=11)
        self.assertEqual(lap.set_pit_status(1), 1)
        self.assertEqual(lap.pit_status, 1)
        self.assertEqual(lap.set_pit_status(3), 3)
        self.assertEqual(lap.pit_status, 3)
        self.assertEqual(lap.set_pit_status(2), 3)
        self.assertEqual(lap.pit_status, 3)
    
    def test_new_lap_data_should_be_written(self):
        # Time trial is never complete -> should always be false
        lap = F12022Lap(lap_number=2, session_type=13)
        # Set values so that they should be true except for TT
        lap.sector_1_ms = 1
        lap.sector_2_ms = 2
        lap.sector_3_ms = 3
        self.assertTrue(lap.new_lap_data_should_be_written(0))
        # Set session type to non-time-trial (5 = race)
        lap.session_type = 5
        self.assertFalse(lap.new_lap_data_should_be_written(0))
        # Non-null value should be false
        self.assertTrue(lap.new_lap_data_should_be_written(5))
        # Not all sectors set is never complete
        lap.sector_3_ms = None
        self.assertTrue(lap.new_lap_data_should_be_written(0))
    
    def test_lap_update(self):
        # Start time trial lap (avoids the in/out lap dependencies)
        lap = F12022Lap(lap_number=2, session_type=13)
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
    
    def test_can_be_synced_to_f1laps(self):
        lap = F12022Lap(lap_number=2, session_type=13)
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

        

        


if __name__ == '__main__':
    unittest.main()