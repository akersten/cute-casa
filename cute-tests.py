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
        h = self.z.createHousehold("testHousehold")
        self.assertTrue(self.z.getHousehold("testHousehold") is not None, "No household came back from the database.")
        self.assertTrue(self.z.getHousehold("testHousehold") is h, "Household comparison failed.")
        pass

    def test_getHouseholdAdvanced(self):
        """No househould should be returned for an invalid index, households should not be transposed."""
        h1 = self.z.createHousehold("h1")
        h2 = self.z.createHousehold("h2")
        h3 = self.z.createHousehold("h3")

        self.assertTrue(h1 is not h2)
        self.assertTrue(h2 is not h3)

        # Theoretically, the below can be replaced with "is h1" based on transitive property above, but
        # I want to be explicit.
        self.assertTrue(self.z.getHousehold('h1') is not h2)
        self.assertTrue(self.z.getHousehold('h1') is not h3)

        self.assertTrue(self.z.getHousehold('h1') is h1)
        self.assertTrue(self.z.getHousehold('h2') is h2)
        self.assertTrue(self.z.getHousehold('h3') is h3)

        self.assertTrue(self.z.getHousehold('bogus') is None)


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