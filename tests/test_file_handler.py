from unittest import TestCase
from unittest.mock import MagicMock

from lib.file_handler import ConfigFile

class FileHandlerTest(TestCase):

    def setUp(self):
        self.user_api_key_input = "vettel4tw"
        self.config = ConfigFile()
        self.config.write = MagicMock()
        self.config.read = MagicMock(return_value="API_KEY=%s" % self.user_api_key_input)

    def test_file_handler_read(self):
        api_key = self.config.get_api_key()
        self.assertEqual(api_key, self.user_api_key_input)

    def test_file_handler_write(self):
        self.config.set_api_key("test")


if __name__ == '__main__':
    unittest.main()