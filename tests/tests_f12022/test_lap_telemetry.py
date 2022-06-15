from unittest import TestCase

from receiver.f12022.telemetry import F12022LapTelemetry


class F12022LapTelemetryTest(TestCase):
    def test_create(self):
        telemetry = F12022LapTelemetry(lap_number=1, session_type=11)
        self.assertEqual(telemetry.lap_number, 1)
        self.assertEqual(telemetry.frame_dict, {})
    
    def test_update(self):
        telemetry = F12022LapTelemetry(lap_number=2, session_type=11)
        self.assertEqual(telemetry.frame_dict, {})
        # First update creates frame
        telemetry.update(telemetry_dict = {
            "lap_distance": 5,
            "frame_identifier": 1000,
            "lap_time": 50,
        })
        self.assertEqual(telemetry.frame_dict, {1000: [5, 50, None, None, None, None, None, None]})
        # Second update does nothing
        telemetry.update(telemetry_dict = {
            "lap_distance": 5,
            "frame_identifier": 1000,
            "lap_time": 50,
        })
        self.assertEqual(telemetry.frame_dict, {1000: [5, 50, None, None, None, None, None, None]})
    
    def test_clean_frame_popped_frame_doesnt_get_readded(self):
        telemetry = F12022LapTelemetry(lap_number=2, session_type=11)
        frame_id = 1000
        # First add a frame
        telemetry.update(telemetry_dict = {
            "lap_distance": 5,
            "frame_identifier": frame_id,
        })
        self.assertTrue(telemetry.frame_dict[frame_id])
        # Now remove it
        telemetry.remove_frame(frame_id)
        self.assertEqual(telemetry.frame_dict, {})
        # Adding it again should not create it
        telemetry.update(telemetry_dict = {
            "lap_distance": 5,
            "frame_identifier": frame_id,
        })
        self.assertEqual(telemetry.frame_dict, {})
    
    def test_clean_frame_no_negative_distance(self):
        telemetry = F12022LapTelemetry(lap_number=2, session_type=11)
        # Add a new frame to set last_lap_distance
        telemetry.update(telemetry_dict = {
            "lap_distance": 10,
            "frame_identifier": 1000,
        })
        self.assertEqual(telemetry.last_lap_distance, 10)
        # A negative distance should not be added
        telemetry.update(telemetry_dict = {
            "lap_distance": -5,
            "frame_identifier": 1000,
        })
        self.assertEqual(telemetry.frame_dict, {})
        self.assertEqual(telemetry.last_lap_distance, None)

    def test_process_flashback_event(self):
        telemetry = F12022LapTelemetry(lap_number=2, session_type=11)
        # Add a few frames
        telemetry.update(telemetry_dict = {
            "lap_distance": 10,
            "frame_identifier": 1000,
        })
        telemetry.update(telemetry_dict = {
            "lap_distance": 11,
            "frame_identifier": 1001,
        })
        telemetry.update(telemetry_dict = {
            "lap_distance": 12,
            "frame_identifier": 1002,
        })
        telemetry.update(telemetry_dict = {
            "lap_distance": 13,
            "frame_identifier": 1003,
        })
        self.assertEqual(len(telemetry.frame_dict), 4)
        self.assertEqual(telemetry.last_lap_distance, 13)
        # Flashback
        telemetry.process_flashback_event(1001)
        self.assertEqual(len(telemetry.frame_dict), 1)
        self.assertEqual(telemetry.last_lap_distance, None)

    

if __name__ == '__main__':
    unittest.main()