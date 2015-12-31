import unittest

from src import zdb

class zdbHouseholdTests(unittest.TestCase):

    def setUp(self):
        self.z = zdb.Zdb('secret/tests.zdb')

    def tearDown(self):
        self.z.teardown()

    def test_getInvalidHouseholdIsNone(self):
        """Test getHousehold."""
        self.assertTrue(self.z.getHousehold(None) is None, "An invalid value passed to getHousehold returns None.")
        self.assertTrue(self.z.getHousehold('invalid val') is None, "An invalid value passed to getHousehold returns None.")

    def test_addDuplicateHousehold(self):
        pass

    def test_getHouseholdBasic(self):
        """Just creates a household and gets it back, a basic test."""
        pass
    
    def test_HouseholdCreatedIsHouseholdRetrieved(self):
        """A household created in the database must be able to be looked up with the returned object handle."""

        # householdID not important, pick whatever constants you like.
        house1 = self.z.createHousehold(42)
        house2 = self.z.createHousehold(41)
        self.assertTrue(house1 is not None, "Household returned from createHousehold was None.")
        self.assertTrue(house2 is not None, "Household returned from createHousehold was None.")
        self.assertTrue(house1 is self.z.getHousehold(42))
        self.assertTrue(house2 is self.z.getHousehold(41))


if __name__ == '__main__':
    unittest.main()