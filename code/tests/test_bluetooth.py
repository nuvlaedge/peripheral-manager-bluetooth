import mock
import unittest

from bluetooth_manager.bluetooth_manager import main


class TestBluetooth(unittest.TestCase):

    @unittest.skip("dummy test")
    def test_main(self):
        """Dummy test."""
        main = mock.Mock()
        main.return_value = None
        assert None is main()
