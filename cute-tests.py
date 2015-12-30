import unittest

from src import zdb

class zdbHouseholdTests(unittest.TestCase):

    lastZ = None # Todo: clean this up

    def setup_zdb(self):
        """Set up ZDB object."""
        self.lastZ = zdb.Zdb('secret/tests.db')
        return self.lastZ

    def teardown_zdb(self, zdb):
        """Teardown ZDB object."""
        if not zdb is None:
            zdb.teardown()
        if not self.lastZ is None:
            self.lastZ.teardown()

    def test_getInvalidHouseholdIsNone(self):
        """Test getHousehold."""
        self.teardown_zdb(None)
        z = self.setup_zdb()
        self.assertTrue(z.getHousehold(None) is None, "An invalid value passed to getHousehold returns None.")
        self.assertTrue(z.getHousehold('invalid val') is None, "An invalid value passed to getHousehold returns None.")
        self.teardown_zdb(z)

    def test_addDuplicateHousehold(self):
        pass

    def test_HouseholdCreatedIsHouseholdRetrieved(self):
        """A household created in the database must be able to be looked up with the returned object handle."""
        self.teardown_zdb(None)
        z = self.setup_zdb()

        # householdID not important, pick whatever constants you like.
        house1 = z.createHousehold(42)
        house2 = z.createHousehold(41)
        self.assertTrue(house1 is z.getHousehold(42))
        self.assertTrue(house2 is z.getHousehold(41))
        self.assertTrue(False)
        self.teardown_zdb(z)


if __name__ == '__main__':
    unittest.main()