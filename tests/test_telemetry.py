from unittest import TestCase
#from unittest.mock import MagicMock, patch

from receiver.telemetry import Telemetry


class TelemetryTests(TestCase):

    def test_start_telemetry(self):
        # initialize
        telemetry = Telemetry()
        self.assertEqual(telemetry.current_lap, None)
        self.assertEqual(telemetry.current_lap_number, None)
        self.assertEqual(telemetry.lap_dict, {})
        # start new lap
        telemetry.start_new_lap(1)
        self.assertEqual(telemetry.current_lap.number, 1)
        self.assertEqual(telemetry.current_lap_number, 1)
        self.assertEqual(telemetry.lap_dict[1], telemetry.current_lap)
        self.assertEqual(telemetry.current_lap.frame_dict, {})
        # start same lap again - no problem
        telemetry.start_new_lap(1)
        self.assertEqual(telemetry.current_lap.number, 1)
        self.assertEqual(telemetry.current_lap.frame_dict, {})
        # start new lap
        telemetry.start_new_lap(2)
        self.assertEqual(telemetry.current_lap.number, 2)
        self.assertEqual(telemetry.current_lap_number, 2)
        self.assertEqual(telemetry.lap_dict[2], telemetry.current_lap)
        self.assertEqual(telemetry.lap_dict[1].number, 1)
        self.assertEqual(telemetry.current_lap.frame_dict, {})
        # a third lap deletes lap 1
        telemetry.start_new_lap(3)
        self.assertEqual(telemetry.current_lap.number, 3)
        self.assertEqual(telemetry.lap_dict[3], telemetry.current_lap)
        self.assertEqual(telemetry.lap_dict[2].number, 2)
        self.assertEqual(1 in telemetry.lap_dict, False)
        self.assertEqual(2 in telemetry.lap_dict, True)

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

    def test_get_telemetry_api_dict(self):
        telemetry = Telemetry()
        telemetry.start_new_lap(1)
        telemetry.set(1000, speed=200, lap_distance=10)
        distance_dict = telemetry.get_telemetry_api_dict(1)
        self.assertEqual(distance_dict, {10: [None, 200, None, None, None, None, None]})
        distance_dict = telemetry.get_telemetry_api_dict(2)
        self.assertEqual(distance_dict, None)


class TelemetryLapTests(TestCase):

    def test_is_complete_lap(self):
        telemetry = Telemetry()
        telemetry.start_new_lap(1)
        self.assertEqual(telemetry.current_lap.is_complete_lap(), False)
        big_dict = dict.fromkeys(range(1, 1002))
        telemetry.current_lap.distance_dict = big_dict
        self.assertEqual(telemetry.current_lap.is_complete_lap(), True)

    def test_update_distance_dict(self):
        telemetry = Telemetry()
        telemetry.start_new_lap(1)
        tl = telemetry.current_lap
        # updating dicts on an non-existing frame should not do anything
        tl.update_distance_dict(1000)
        self.assertEqual(tl.distance_dict, {})
        # updating on an existing frame but no distance should not do anything
        # .set calls distance dict too
        telemetry.set(1000, speed=300, brake=0.01)
        self.assertEqual(tl.distance_dict, {})
        # now let's update it
        telemetry.set(1000, speed=300, brake=0.01, lap_distance=50)
        self.assertEqual(tl.distance_dict, {
            50: [None, 300, 0.01, None, None, None, None]
            })
        # additional one with all values
        telemetry.set(1001, speed=299, brake=0.5, lap_distance=62, lap_time=4301, throttle=0.3, gear=3, drs=0, steer=-0.4)
        self.assertEqual(tl.distance_dict, {
            50: [None, 300, 0.01, None, None, None, None],
            62: [4301, 299, 0.5, 0.3, 3, -0.4, 0]
            })

    def test_clean_up_flashbacks(self):
        telemetry = Telemetry()
        telemetry.start_new_lap(1)
        tl = telemetry.current_lap
        telemetry.set(1000, speed=300, lap_distance=50)
        telemetry.set(1001, speed=301, lap_distance=51)
        telemetry.set(1002, speed=302, lap_distance=52)
        telemetry.set(1003, speed=303, lap_distance=53)
        telemetry.set(1004, speed=304, lap_distance=54)
        telemetry.set(1005, speed=305, lap_distance=55)
        telemetry.set(1006, speed=306, lap_distance=56)
        telemetry.set(1007, speed=307, lap_distance=57)
        self.assertEqual(tl.distance_dict, {
            50: [None, 300, None, None, None, None, None],
            51: [None, 301, None, None, None, None, None],
            52: [None, 302, None, None, None, None, None],
            53: [None, 303, None, None, None, None, None],
            54: [None, 304, None, None, None, None, None],
            55: [None, 305, None, None, None, None, None],
            56: [None, 306, None, None, None, None, None],
            57: [None, 307, None, None, None, None, None]
            })
        # flashback
        telemetry.set(1008, speed=202, lap_distance=52)
        self.assertEqual(tl.distance_dict, {
            50: [None, 300, None, None, None, None, None],
            51: [None, 301, None, None, None, None, None],
            52: [None, 202, None, None, None, None, None]
            })
        telemetry.set(1009, speed=203, lap_distance=53)
        self.assertEqual(tl.distance_dict, {
            50: [None, 300, None, None, None, None, None],
            51: [None, 301, None, None, None, None, None],
            52: [None, 202, None, None, None, None, None],
            53: [None, 203, None, None, None, None, None]
            })
        
        

