from unittest import TestCase

from receiver.f12022.session import F12022Session


class F12022SessionTest(TestCase):
    def test_create(self):
        session = F12022Session(
            "f1laps_key_123",
            True, # with telemetry
            "uid_123",
            10, # session type = race
            1, # track id
            False, # offline
            90, # ai difficulty
            1 # weather
        )
        self.assertEqual(session.session_udp_uid, "uid_123")
        self.assertEqual(session.game_version, "f12022")
        self.assertEqual(session.session_type_name, "race")
        


if __name__ == '__main__':
    unittest.main()