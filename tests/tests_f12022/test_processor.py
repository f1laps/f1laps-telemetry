from unittest import TestCase
from unittest.mock import patch, MagicMock

from receiver.f12022.processor import F12022Processor
from receiver.f12022.session import F12022Session


class F12022SessionTest(TestCase):
    def test_setup_packet_via_generic_process(self):
        """ Test setup package sets session's setup. Use main process method to test cover it too. """
        setup = {
            "packet_type": "setup",
            "front_wing": 1,
            "rear_wing": 1
        }
        processor = F12022Processor("key_123", True)
        processor.session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        success = processor.process_serialized_packet(setup)
        self.assertTrue(success)
        self.assertEqual(len(processor.session.setup), 20)
        self.assertEqual(processor.session.setup["front_wing"], 1)

    def test_process_telemetry_packet_new_lap(self):
        processor = F12022Processor("key_123", True)
        processor.session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
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
        processor.session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        self.assertEqual(len(processor.session.participants), 0)
        self.assertEqual(processor.session.team_id, None)
        # Set team_id and participants
        # Test team ID 0 specifically as it's an edge case (none/0)
        processor.process_participant_data({
            "packet_type": "participants",
            "team_id": 0,
            "num_participants": 2,
            "participants": [
                {"driver": 5, "driver_index": 1, "name": "Seb", "team": 1},
                {"driver": 6, "driver_index": 2, "name": "Lewis", "team": 2},
            ]
        })
        self.assertEqual(len(processor.session.participants), 2)
        self.assertEqual(processor.session.team_id, 0)
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
        self.assertEqual(processor.session.team_id, 0)
    
    @patch("receiver.f12022.processor.F12022Session.sync_to_f1laps")
    def test_process_final_classifictation_packet(self, mock_f1l_sync):
        processor = F12022Processor("key_123", True)
        processor.session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        # Add 2 participants
        processor.process_participant_data({
            "packet_type": "participants",
            "team_id": 2,
            "num_participants": 2,
            "participants": [
                {"driver": 5, "driver_index": 0, "name": "Seb", "team": 1},
                {"driver": 6, "driver_index": 1, "name": "Lewis", "team": 2},
            ]
        })
        # Send classification
        classification_data = {
            "packet_type": "final_classification",
            "finish_position": 3,
            "result_status": 6,
            "points": 15,
            "all_participants_results": {
                "0": {
                    "finish_position": 3,
                    "result_status": 6,
                    "points": 15,
                    "grid_position": 4,
                    "lap_time_best": 66666,
                    "penalties_number": 1,
                    "race_time_total": 222222,
                    "penalties_time_total": 11,
                },
                "1": {
                    "finish_position": 1,
                    "result_status": 3,
                    "points": 25,
                    "grid_position": 5,
                    "lap_time_best": 77777,
                    "penalties_number": 0,
                    "race_time_total": 222000,
                    "penalties_time_total": 0,
                }
            }
        }
        processor.process_final_classifictation_packet(classification_data)
        self.assertEqual(processor.session.finish_position, 3)
        self.assertEqual(processor.session.result_status, 6)
        self.assertEqual(processor.session.points, 15)
        self.assertEqual(processor.session.participants[0].finish_position, 3)
        self.assertEqual(processor.session.participants[1].finish_position, 1)
        self.assertEqual(processor.session.participants[0].penalties_number, 1)
        self.assertEqual(processor.session.participants[1].penalties_number, 0)
        mock_f1l_sync.assert_called_once_with(lap_number=None, sync_entire_session=True)

    @patch("receiver.f12022.processor.F12022Session.get_current_lap")
    def test_process_flashback_event_packet(self, mock_lap):
        processor = F12022Processor("key_123", True)
        processor.session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        mock_flashback = MagicMock()
        mock_lap.return_value.process_flashback_event = mock_flashback
        processor.process_event_packet({
            "packet_type": "event",
            "event_type": "flashback",
            "frame_identifier": 123,
            "session_time": 222222
        })
        mock_lap.assert_called_once_with()
        mock_flashback.assert_called_once_with(123)
    
    @patch("receiver.f12022.processor.F12022Penalty.send_to_f1laps")
    def test_process_flashback_event_packet(self, mock_f1l_sync):
        processor = F12022Processor("key_123", True)
        processor.session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        processor.process_event_packet({
            "packet_type": "event",
            "event_type": "penalty",
            "penalty_type": 1,
            "infringement_type": 2,
            "vehicle_index": 3,
            "other_vehicle_index": 4,
            "time_spent_gained": 55,
            "lap_number": 6,
            "places_gained": 7
        })
        mock_f1l_sync.assert_called_once_with()
    
    def test_process_car_status_packet(self):
        processor = F12022Processor("key_123", True)
        processor.session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        processor.session.add_lap(1)
        processor.process_car_status_packet({
            "packet_type": "car_status",
            "tyre_compound_visual": "soft"
        })
        self.assertEqual(processor.session.lap_list[1].tyre_compound_visual, "soft")
    
    

if __name__ == '__main__':
    unittest.main()