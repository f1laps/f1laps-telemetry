from unittest import TestCase
from unittest.mock import MagicMock

from lib.file_handler import ConfigFile, get_path_executable_parent, get_path_temporary

class FileHandlerTest(TestCase):

    def setUp(self):
        self.user_api_key_input = "vettel4tw"
        self.config = ConfigFile()

    def test_get(self):
        # Clean any old values
        self.config.set("API_KEY", None)
        self.config.set("UDP_BROADCAST_ENABLED", None)
        # Test various gets
        self.assertEqual(self.config.get("API_KEY"), None)
        self.assertEqual(self.config.get("UDP_BROADCAST_ENABLED"), None)
        self.config.load()
        self.assertEqual(self.config.get("API_KEY"), None)
        self.assertEqual(self.config.get("UDP_BROADCAST_ENABLED"), None)
        # Set first value
        self.config.set("API_KEY", "vettel4tw")
        self.assertEqual(self.config.get("API_KEY"), "vettel4tw")
        self.assertEqual(self.config.get("UDP_BROADCAST_ENABLED"), None)
        # Set second value
        self.config.set("UDP_BROADCAST_ENABLED", True)
        self.assertEqual(self.config.get("API_KEY"), "vettel4tw")
        self.assertEqual(self.config.get("UDP_BROADCAST_ENABLED"), True)
        # Load again
        self.config.load()
        self.assertEqual(self.config.get("API_KEY"), "vettel4tw")
        self.assertEqual(self.config.get("UDP_BROADCAST_ENABLED"), True)

    def test_get_path_executable_parent(self):
        path = get_path_executable_parent("f1laps_configuration.txt")
        self.assertTrue("f1laps_configuration.txt" in path)

    def test_get_path_temporary(self):
        path = get_path_temporary("f1laps_configuration.txt")
        self.assertTrue("f1laps_configuration.txt" in path)



if __name__ == '__main__':
    unittest.main()