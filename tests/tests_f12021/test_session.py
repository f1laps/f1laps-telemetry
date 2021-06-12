from unittest import TestCase

from receiver.f12021.session import F12021Session


class F12021SessionTest(TestCase):

    def test_complete_lap(self):
        session = F12021Session(123)
        session.complete_lap(lap_number = 1, sector_1_ms = 11111, sector_2_ms = 22222, sector_3_ms = 33333, tyre_visual = 16)
        self.assertEqual(session.lap_list, {1: {'lap_number': 1, 'sector_1_ms': 11111, 'sector_2_ms': 22222, 'sector_3_ms': 33333, 'tyre_compound_visual': 16}})

    def test_get_track_name(self):
        session = F12021Session(123)
        session.track_id = 5
        self.assertEqual(session.get_track_name(), "Monaco")

    def test_get_session_type(self):
        session = F12021Session(123)
        session.session_type = 7
        self.assertEqual(session.get_session_type(), "qualifying_3")
        


if __name__ == '__main__':
    unittest.main()