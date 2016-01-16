import unittest
from src.household.household import Household

class Tests_Household(unittest.TestCase):
    """Tests the Household object."""

    def test_init(self):
        """
        Basic household creation tests. A household cannot have an id that is None or blank. Household ids must be str
        type.
        """
        with self.assertRaises(TypeError):
            Household(None)
        with self.assertRaises(TypeError):
            Household(100)
        with self.assertRaises(ValueError):
            Household('')

        Household('householdId')
