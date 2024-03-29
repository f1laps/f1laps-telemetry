from unittest import TestCase
from unittest.mock import MagicMock, patch

from receiver.game_version import parse_game_version_from_udp_packet


class GameVersionTest(TestCase):

    @patch('receiver.game_version.CrossGamePacketHeader')
    def test_parse_game_version_from_udp_packet(self, mock_header):
        mock_header.from_buffer_copy.return_value = MagicMock(packetFormat=2020)
        game_version = parse_game_version_from_udp_packet("doesntmatter")
        self.assertEqual(game_version, "f12020")

    @patch('receiver.game_version.CrossGamePacketHeader')
    def test_parse_game_version_from_udp_packet_unsupported_returns_snone(self, mock_header):
        mock_header.from_buffer_copy.return_value = MagicMock(packetFormat=2019)
        game_version = parse_game_version_from_udp_packet("doesntmatter")
        self.assertEqual(game_version, None)


if __name__ == '__main__':
    unittest.main()