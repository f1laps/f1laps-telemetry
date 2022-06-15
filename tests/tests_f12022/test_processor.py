from unittest import TestCase

from receiver.f12022.processor import F12022Processor
from receiver.f12022.session import F12022Session


class F12022LapTelemetryTest(TestCase):
    def test_process_telemetry_packet_new_lap(self):
        processor = F12022Processor("key_123", True)
        processor.session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1)
        processor.session.add_lap(1)
        processor.process_telemetry_packet({
            "packet_type": "telemetry",
            "frame_identifier": 1000,
            "speed": 100,
            "brake": 0,
            "throttle": 0.9,
            "gear": 4,
            "steer": 0.1,
            "drs": 0,
        })
        self.assertEqual(processor.session.get_current_lap().telemetry.frame_dict, {1000: [None, None, 100, 0, 0.9, 4, 0.1, 0]})
    
    def test_process_participant_data(self):
        processor = F12022Processor("key_123", True)
        processor.session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1)
        self.assertEqual(len(processor.session.participants), 0)
        self.assertEqual(processor.session.team_id, None)
        # Set team_id and participants
        processor.process_participant_data({
            "packet_type": "participants",
            "team_id": 2,
            "num_participants": 2,
            "participants": [
                {"driver": 5, "driver_index": 1, "name": "Seb", "team": 1},
                {"driver": 6, "driver_index": 2, "name": "Lewis", "team": 2},
            ]
        })
        self.assertEqual(len(processor.session.participants), 2)
        self.assertEqual(processor.session.team_id, 2)
        # Try again, should not change anything
        processor.process_participant_data({
            "packet_type": "participants",
            "team_id": 2,
            "num_participants": 2,
            "participants": [
                {"driver": 5, "index": 1, "name": "Seb", "team_id": 1},
                {"driver": 6, "index": 2, "name": "Lewis", "team_id": 2},
            ]
        })
        self.assertEqual(len(processor.session.participants), 2)
        self.assertEqual(processor.session.team_id, 2)
    
    
    

if __name__ == '__main__':
    unittest.main()