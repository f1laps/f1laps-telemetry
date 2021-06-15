from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.f12020.api import F1LapsAPI
import config


class F1LapsAPITest(TestCase):

    @patch('platform.release')
    @patch('platform.system')
    def test_get_headers(self, mock_system, mock_release):
        mock_system.return_value = "F1Laps Test Runner"
        mock_release.return_value = "2021.02.28"
        headers = F1LapsAPI("vettel4tw", "f12020")._get_headers()
        self.assertEqual(headers, {
            'Content-Type'      : 'application/json',
            'Authorization'     : 'Token vettel4tw',
            'X-F1Laps-App'      : 'F1Laps Telemetry v%s' % config.VERSION,
            'X-F1Laps-Platform' : "F1Laps Test Runner 2021.02.28"
            })


if __name__ == '__main__':
    unittest.main()