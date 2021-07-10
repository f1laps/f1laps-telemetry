from unittest import TestCase

from receiver.f12021.processor import F12021Processor


class F12021ProcessorTest(TestCase):

    def test_init_processor(self):
        processor = F12021Processor("mockapikey", True)
        self.assertEqual(processor.session, None)
        self.assertEqual(processor.f1laps_api_key, "mockapikey")
        self.assertEqual(processor.telemetry_enabled, True)


if __name__ == '__main__':
    unittest.main()