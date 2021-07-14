from unittest import TestCase

from receiver.f12021.telemetry import F12021Telemetry
from receiver.telemetry_base import KEY_INDEX_MAP


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

