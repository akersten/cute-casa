import unittest

from src.user.user import User


class Tests_User(unittest.TestCase):
    """Tests the User object."""

    def test_init_invalidId(self):
        """A user cannot have an id that is None or blank."""
        with self.assertRaises(ValueError):
            User('')
        with self.assertRaises(ValueError):
            User(None)

    def test_init_basic(self):
        """Basic user creation tests."""
        User(41)

        #TODO