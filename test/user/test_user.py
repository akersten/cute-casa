import unittest

from src.user.user import User


class Tests_User(unittest.TestCase):
    """Tests the User object."""

    def test_init(self):
        """
        Basic user creation tests. A user cannot have an id or displayname that is None or blank. User ids and
        displaynames must be str type.
        """

        with self.assertRaises(TypeError):
            User(None, 'displayname')
        with self.assertRaises(TypeError):
            User(100, 'displayname')

        with self.assertRaises(ValueError):
            User('', 'displayname')


        with self.assertRaises(TypeError):
            User('userId', None)
        with self.assertRaises(TypeError):
            User('userId', 100)

        with self.assertRaises(ValueError):
            User('userId', '')

        User('100', 'displayname')