import unittest

import src.core.notification.yo.yoer as yo

class Tests_Yoer(unittest.TestCase):
    """Tests the Yoer object."""

    def test_init(self):
        """Tests the Yoer constructor with both invalid and "valid" (fake API key) data."""

        with self.assertRaises(TypeError):
            y = yo.Yoer(None)
            y = yo.Yoer(1234)
        with self.assertRaises(ValueError):
            y = yo.Yoer("")

        y = yo.Yoer('test')

    def test_yo(self):
        """Tests the send Yo functionality."""
        y = yo.Yoer("TEST")

        with self.assertRaises(TypeError):
            y.yo(None, "TEST")
            y.yo(1234, "TEST")
            y.yo("TEST", None)
            y.yo("TEST", 1234)
        with self.assertRaises(ValueError):
            y.yo("", "TEST")
            y.yo("TEST", "")
            y.yo("TEST", "1234567890123456789012345678901")

        # Test a maximum length message and a short message.
        y.yo("TEST", "123456789012345678901234567890")
        y.yo("TEST", "1")

