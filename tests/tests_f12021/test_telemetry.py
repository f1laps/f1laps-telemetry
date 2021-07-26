from unittest import TestCase

from receiver.f12021.telemetry import F12021Telemetry
from receiver.telemetry_base import KEY_INDEX_MAP


class F12021TelemetryTests(TestCase):

    def test_start_telemetry_old_lap(self):
        """ 
        Assert that when we attempt to start Telemetry for a lap that was already collected,
        we don't do it.
        This happens when the Session History Packet starts Telemetry, but is significantly delayed by 1+ laps
        And hence attempts to start an old lap
        """
        telemetry = F12021Telemetry()
        # start new lap
        telemetry.start_new_lap(1)
        self.assertEqual(telemetry.current_lap_number, 1)
        self.assertEqual(telemetry.lap_dict[1].number, 1)
        # start new lap
        telemetry.start_new_lap(2)
        self.assertEqual(telemetry.current_lap_number, 2)
        self.assertEqual(telemetry.lap_dict[2].number, 2)
        # attempt old lap
        telemetry.start_new_lap(1)
        self.assertEqual(telemetry.current_lap_number, 2)
        self.assertEqual(telemetry.lap_dict[2].number, 2)

    def test_process_flashback_event(self):
        telemetry = F12021Telemetry()
        telemetry.start_new_lap(1)
        telemetry.set(1000, speed=300, lap_distance=50)
        telemetry.set(1001, speed=301, lap_distance=51)
        telemetry.set(1002, speed=302, lap_distance=52)
        telemetry.set(1003, speed=303, lap_distance=53)
        self.assertEqual(telemetry.current_lap.last_lap_distance, 53)
        self.assertEqual(telemetry.current_lap.frame_dict, {
            1000: [50, None, 300, None, None, None, None, None],
            1001: [51, None, 301, None, None, None, None, None],
            1002: [52, None, 302, None, None, None, None, None],
            1003: [53, None, 303, None, None, None, None, None],
        })
        telemetry.process_flashback_event(1001)
        self.assertEqual(telemetry.current_lap.frame_dict, {
            1000: [50, None, 300, None, None, None, None, None],
        })
        self.assertEqual(telemetry.current_lap.last_lap_distance, None)
        telemetry.set(1001, speed=301, lap_distance=52)
        self.assertEqual(telemetry.current_lap.last_lap_distance, 52)


class F12021TelemetryLapTests(TestCase):

    def test_clean_frame_outlap_pre_line_negative_distances(self):
        """ 
        In an outlap, when the lap distance is negative, clean any negative distance frames 
        """
        telemetry = F12021Telemetry()
        telemetry.start_new_lap(1)
        tl = telemetry.current_lap
        telemetry.set(1000, speed=300, lap_distance=-100)
        telemetry.set(1001, speed=301, lap_distance=-99)
        telemetry.set(1002, speed=302, lap_distance=-98)
        self.assertEqual(tl.frame_dict, {})
        telemetry.set(1003, speed=303, lap_distance=13)
        self.assertEqual(tl.frame_dict, {
            1003: [13, None, 303, None, None, None, None, None],
        })
        telemetry.set(1004, speed=304, lap_distance=14)
        telemetry.set(1005, speed=305, lap_distance=15)
        self.assertEqual(tl.frame_dict, {
            1003: [13, None, 303, None, None, None, None, None],
            1004: [14, None, 304, None, None, None, None, None],
            1005: [15, None, 305, None, None, None, None, None],
        })

    def test_clean_frame_outlap_pre_line_positive_distances(self):
        """ 
        In an outlap, when the lap distance is positive, clean any positive distance frames pre line
        """
        telemetry = F12021Telemetry()
        telemetry.start_new_lap(1)
        tl = telemetry.current_lap
        telemetry.set(1000, speed=300, lap_distance=4400)
        telemetry.set(1001, speed=301, lap_distance=4401)
        telemetry.set(1002, speed=302, lap_distance=4402)
        self.assertEqual(tl.frame_dict, {
            1000: [4400, None, 300, None, None, None, None, None],
            1001: [4401, None, 301, None, None, None, None, None],
            1002: [4402, None, 302, None, None, None, None, None],
        })
        telemetry.set(1003, speed=303, lap_distance=13)
        self.assertEqual(tl.frame_dict, {
            1003: [13, None, 303, None, None, None, None, None],
        })
        telemetry.set(1004, speed=304, lap_distance=14)
        telemetry.set(1005, speed=305, lap_distance=15)
        self.assertEqual(tl.frame_dict, {
            1003: [13, None, 303, None, None, None, None, None],
            1004: [14, None, 304, None, None, None, None, None],
            1005: [15, None, 305, None, None, None, None, None],
        })

    def test_clean_frame_outlap_pre_line_positive_distances_no_first_distance(self):
        """ 
        Same as above, but without a first lap distance because the first frame didn't get a lap packet in time
        """
        telemetry = F12021Telemetry()
        telemetry.start_new_lap(1)
        tl = telemetry.current_lap
        tl.last_lap_distance = 4500 # greater than distance we set next
        telemetry.set(1000, speed=300)
        telemetry.set(1001, speed=300, lap_distance=100)
        self.assertEqual(tl.frame_dict, {1000: [None, None, 300, None, None, None, None, None]})

    def test_clean_frame_inlap_post_line_positive_distances(self):
        """ 
        In an inlap after race end, when the lap distance is positive, clean any new frames
        """
        telemetry = F12021Telemetry()
        telemetry.start_new_lap(1)
        tl = telemetry.current_lap
        telemetry.set( 100, speed=297, lap_distance=13)
        telemetry.set( 101, speed=298, lap_distance=14)
        telemetry.set( 102, speed=299, lap_distance=15)
        telemetry.set(1000, speed=300, lap_distance=4400)
        telemetry.set(1001, speed=301, lap_distance=4401)
        telemetry.set(1002, speed=302, lap_distance=4402)
        self.assertEqual(tl.frame_dict, {
             100: [  13, None, 297, None, None, None, None, None],
             101: [  14, None, 298, None, None, None, None, None],
             102: [  15, None, 299, None, None, None, None, None],
            1000: [4400, None, 300, None, None, None, None, None],
            1001: [4401, None, 301, None, None, None, None, None],
            1002: [4402, None, 302, None, None, None, None, None],
        })
        telemetry.set(1003, speed=303, lap_distance=13)
        telemetry.set(1004, speed=304, lap_distance=14)
        telemetry.set(1005, speed=305, lap_distance=15)
        print(tl.frame_dict)
        self.assertEqual(tl.frame_dict, {
             100: [  13, None, 297, None, None, None, None, None],
             101: [  14, None, 298, None, None, None, None, None],
             102: [  15, None, 299, None, None, None, None, None],
            1000: [4400, None, 300, None, None, None, None, None],
            1001: [4401, None, 301, None, None, None, None, None],
            1002: [4402, None, 302, None, None, None, None, None],
        })

