from unittest import TestCase
#from unittest.mock import MagicMock, patch

from receiver.telemetry import Telemetry


class SessionBaseTests(TestCase):

    def test_start_telemetry(self):
        # initialize
        telemetry = Telemetry()
        self.assertEqual(telemetry.current_lap, None)
        # start new lap
        telemetry.start_new_lap(1)
        self.assertEqual(telemetry.current_lap.number, 1)
        self.assertEqual(telemetry.current_lap.frame_dict, {})
        # start same lap again - no problem
        telemetry.start_new_lap(1)
        self.assertEqual(telemetry.current_lap.number, 1)
        self.assertEqual(telemetry.current_lap.frame_dict, {})
        # start new lap
        telemetry.start_new_lap(2)
        self.assertEqual(telemetry.current_lap.number, 2)
        self.assertEqual(telemetry.current_lap.frame_dict, {})

    def test_set_frame_value(self):
        telemetry = Telemetry()
        # test on empty value - should not raise but log warning
        telemetry.set(1000, speed=200)
        self.assertEqual(telemetry.current_lap, None)
        # start lap
        telemetry.start_new_lap(1)
        telemetry.set(1000, speed=200)
        self.assertEqual(telemetry.current_lap.frame_dict[1000]["speed"], 200)
        # setting the same value again should not change
        # but new values should
        telemetry.set(1000, speed=300, brake=0.05)
        self.assertEqual(telemetry.current_lap.frame_dict[1000]["speed"], 200)
        self.assertEqual(telemetry.current_lap.frame_dict[1000]["brake"], 0.05)
        # but a new frame sets
        telemetry.set(1001, speed=300, brake=0.04)
        self.assertEqual(telemetry.current_lap.frame_dict[1001]["speed"], 300)
        self.assertEqual(telemetry.current_lap.frame_dict[1001]["brake"], 0.04)
        # new lap, new values
        telemetry.start_new_lap(2)
        telemetry.set(1000, speed=300, brake=0.01)
        self.assertEqual(telemetry.current_lap.frame_dict[1000]["speed"], 300)
        self.assertEqual(telemetry.current_lap.frame_dict[1000]["brake"], 0.01)
