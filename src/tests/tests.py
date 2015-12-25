import unittest

class zdbHouseholdTests(unittest.TestCase):

    def test_HouseholdCreatedIsHouseholdRetrieved(self):
        """A household created in the database must be able to be looked up with the returned object handle."""
        self.assertEqual(2,4)


if __name__ == '__main__':
    unittest.main()