import unittest

from src import zdb


class Tests_zdb_household(unittest.TestCase):

    def setUp(self):
        self.z = zdb.Zdb('secret/tests.zdb')

    def tearDown(self):
        self.z.teardown()

    def test_createHousehold_invalidId(self):
        """Households with a blank ID should not be allowed to be created."""

        with self.assertRaises(ValueError, 'A household cannot have an id of length zero.'):
            self.z.createHousehold('')
        with self.assertRaises(ValueError, 'A household cannot have an id of None.'):
            self.z.createHousehold(None)


    def test_createHousehold_single(self):
        """A household created in the database should have a reference returned from the creation method."""

        h = self.z.createHousehold("testHousehold")
        self.assertTrue(self.z.getHousehold("testHousehold") is not None, "No household came back from the database.")
        self.assertTrue(self.z.getHousehold("testHousehold") is h, "Household comparison failed.")


    def test_createHousehold_multiple(self):
        """A household created in the database must be able to be looked up with the returned object handle."""

        house1 = self.z.createHousehold(42)
        house2 = self.z.createHousehold(41)
        self.assertTrue(house1 is not None, "Household returned from createHousehold was None.")
        self.assertTrue(house2 is not None, "Household returned from createHousehold was None.")
        self.assertTrue(house1 is self.z.getHousehold(42))
        self.assertTrue(house2 is self.z.getHousehold(41))

    def test_createHousehold_duplicateHousehold(self):
        self.z.createHousehold('dupe')

        with self.assertRaises(zdb.DuplicateRecordException, "A DuplicateRecordException should be raised when adding a"
                                                             " household with a duplicate ID."):
            self.z.createHousehold('dupe')


    def test_getHousehold_invalidId(self):
        """Test getting households with invalid Ids."""
        self.assertTrue(self.z.getHousehold(None) is None, "An invalid value passed to getHousehold returns None.")
        self.assertTrue(self.z.getHousehold('') is None, "An invalid value passed to getHousehold returns None.")
        self.assertTrue(self.z.getHousehold('invalid') is None, "An invalid value passed to getHousehold returns None.")

    def test_getHousehold_multiple(self):
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


if __name__ == '__main__':
    unittest.main()