from unittest import TestCase
import time

from receiver.penalty_base import PenaltyBase


class PenaltyBaseTest(TestCase):

    def test_penalty_frame_id(self):
        penalty_1 = PenaltyBase()
        self.assertTrue(penalty_1.frame_id)
        time.sleep(0.001)
        penalty_2 = PenaltyBase()
        self.assertTrue(penalty_2.frame_id > penalty_1.frame_id)