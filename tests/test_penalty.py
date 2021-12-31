from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.penalty_base import PenaltyBase


class PenaltyBaseTest(TestCase):

    def test_time_trial_returns_none(self):
        penalty = PenaltyBase()
        penalty.session = MagicMock()
        penalty.session.is_time_trial.return_value = True
        self.assertIsNone(penalty.send_to_f1laps())

    def test_no_api_class_returns_none(self):
        penalty = PenaltyBase()
        penalty.session = MagicMock()
        penalty.session.is_time_trial.return_value = False
        self.assertIsNone(penalty.send_to_f1laps())
    
    def test_no_session_returns_none(self):
        penalty = PenaltyBase()
        self.assertIsNone(penalty.send_to_f1laps())
    
    def test_no_session_id_create_success(self):
        penalty = PenaltyBase()
        penalty.f1laps_api_class = MagicMock()
        penalty.session = MagicMock(f1_laps_session_id=None)
        penalty.session.send_session_to_f1laps.return_value = True
        penalty.session.is_time_trial.return_value = False
        penalty.session.has_ended.return_value = False
        penalty.infringement_type = 5
        success = penalty.send_to_f1laps()
        self.assertTrue(success)
        penalty.f1laps_api_class.return_value.penalty_create.assert_called_with(f1_laps_session_id=penalty.session.f1_laps_session_id, penalty_type=None, infringement_type=5, vehicle_index=None, other_vehicle_index=None, time_spent_gained=None, lap_number=None, places_gained=None)
    
    def test_no_session_id_create_fails(self):
        penalty = PenaltyBase()
        penalty.f1laps_api_class = MagicMock()
        penalty.session = MagicMock(f1_laps_session_id=None)
        penalty.session.is_time_trial.return_value = False
        penalty.session.send_session_to_f1laps.return_value = False
        self.assertIsNone(penalty.send_to_f1laps())
    
    def test_session_has_ended(self):
        penalty = PenaltyBase()
        penalty.session = MagicMock()
        penalty.session.is_time_trial.return_value = False
        penalty.session.has_ended.return_value = True
        self.assertIsNone(penalty.send_to_f1laps())
    
    def test_success_api(self):
        penalty = PenaltyBase()
        penalty.session = MagicMock()
        penalty.session.is_time_trial.return_value = False
        penalty.session.has_ended.return_value = False
        api_mock = MagicMock()
        api_mock.return_value.penalty_create.return_value = True
        penalty.f1laps_api_class = api_mock
        penalty.infringement_type = 5
        success = penalty.send_to_f1laps()
        self.assertTrue(success)
        penalty.f1laps_api_class.return_value.penalty_create.assert_called_with(f1_laps_session_id=penalty.session.f1_laps_session_id, penalty_type=None, infringement_type=5, vehicle_index=None, other_vehicle_index=None, time_spent_gained=None, lap_number=None, places_gained=None)
    
    def test_error_api(self):
        penalty = PenaltyBase()
        penalty.session = MagicMock()
        penalty.session.is_time_trial.return_value = False
        penalty.session.has_ended.return_value = False
        api_mock = MagicMock()
        api_mock.return_value.penalty_create.return_value = False
        penalty.f1laps_api_class = api_mock
        penalty.infringement_type = 5
        success = penalty.send_to_f1laps()
        self.assertFalse(success)
        penalty.f1laps_api_class.return_value.penalty_create.assert_called_with(f1_laps_session_id=penalty.session.f1_laps_session_id, penalty_type=None, infringement_type=5, vehicle_index=None, other_vehicle_index=None, time_spent_gained=None, lap_number=None, places_gained=None)


if __name__ == '__main__':
    unittest.main()