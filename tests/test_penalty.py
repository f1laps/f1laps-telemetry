from unittest import TestCase

from receiver.penalty_base import PenaltyBase
from receiver.f12021.session import F12021Session
from receiver.f12022.session import F12022Session


class PenaltyBaseTest(TestCase):

    def test_add_to_lap_f12021(self):
        session = F12021Session(123)
        session.start_new_lap(1)
        penalty_1 = PenaltyBase()
        penalty_1.lap_number = 1
        penalty_1.session = session
        penalty_1.add_to_lap()
        self.assertTrue(session.lap_list[1]["penalties"])
        self.assertTrue(penalty_1 in penalty_1.session.lap_list[1]["penalties"])
    
    def test_add_to_lap_f12022(self):
        session = F12022Session("key_123", True, "uid_123", 10, 1, False, 90, 1, 5)
        session.add_lap(1)
        penalty_1 = PenaltyBase()
        penalty_1.lap_number = 1
        penalty_1.session = session
        penalty_1.add_to_lap()
        self.assertTrue(session.lap_list[1].penalties)
        self.assertTrue(penalty_1 in penalty_1.session.lap_list[1].penalties)