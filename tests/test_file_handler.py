from unittest import TestCase
from unittest.mock import MagicMock

from lib.file_handler import ConfigFile, get_path_executable_parent, get_path_temporary

class FileHandlerTest(TestCase):

    def setUp(self):
        self.user_api_key_input = "vettel4tw"
        self.config = ConfigFile()
        self.config._write = MagicMock()
        self.config._read = MagicMock(return_value="API_KEY=%s" % self.user_api_key_input)

    def test_file_handler_read(self):
        api_key = self.config.get_api_key()
        self.assertEqual(api_key, self.user_api_key_input)

    def test_file_handler_write(self):
        self.config.set_api_key("test")

    def test_get_path_executable_parent(self):
        path = get_path_executable_parent("f1laps_configuration.txt")
        self.assertTrue("f1laps_configuration.txt" in path)

    def test_get_path_temporary(self):
        path = get_path_temporary("f1laps_configuration.txt")
        self.assertTrue("f1laps_configuration.txt" in path)



if __name__ == '__main__':
    unittest.main()