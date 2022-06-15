from unittest import TestCase

from requests import session

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
    
    def test_lap_is_complete(self):
        # Time trial is never complete -> should always be false
        lap = F12022Lap(lap_number=2, session_type=13)
        # Set values so that they should be true except for TT
        lap.sector_1_ms = 1
        lap.sector_2_ms = 2
        lap.sector_3_ms = 3
        self.assertFalse(lap.lap_is_complete(0))
        # Set session type to non-time-trial (5 = race)
        lap.session_type = 5
        self.assertTrue(lap.lap_is_complete(0))
        # Non-null value should be false
        self.assertFalse(lap.lap_is_complete(5))
        # Not all sectors set is never complete
        lap.sector_3_ms = None
        self.assertFalse(lap.lap_is_complete(0))

        


if __name__ == '__main__':
    unittest.main()