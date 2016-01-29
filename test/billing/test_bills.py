# Be sure that the values from individual contributions add up to the total calculated liability.


import unittest
from src.billing._bills import Bill, BillGroup

class Tests_Bill(unittest.TestCase):
    """Tests the Bill object."""

    def test_init(self):
        """
        Bill constructor.
        """
        b = Bill()
        self.assertTrue(len(b.getAdjustments()) == 0, 'A new bill should not already have adjustments.')
        self.assertTrue(b.charge == 0, 'A new bill should not already have a charge.')
        self.assertTrue(b.getTotal() == 0, 'A new bill should have a total of 0.')

    def test_addAdjustment(self):
        """
        Adjustments with correct parameters should be able to be added to the bill.
        """
        b = Bill()

        with self.assertRaises(TypeError):
            b.addAdjustment(None, '')
        with self.assertRaises(TypeError):
            b.addAdjustment('', '')
        with self.assertRaises(TypeError):
            b.addAdjustment(123.45, '')

        self.assertTrue(len(b.getAdjustments()) == 0, 'Bad adjustments should not be added to a bill.')

        b.addAdjustment(100, 'Adjustment 1')
        b.addAdjustment(200, 'Adjustment 2')
        b.addAdjustment(-50, 'Adjustment 3')
        b.addAdjustment(0, 'Adjustment 4')

        self.assertTrue(len(b.getAdjustments()) == 4, 'Adjustments should be added to bill.')
        self.assertTrue(b.getAdjustments()[0][0] == 100, 'Adjustment amount is off.')
        self.assertTrue(b.getAdjustments()[1][0] == 200, 'Adjustment amount is off.')
        self.assertTrue(b.getAdjustments()[0][1] == 'Adjustment 1', 'Adjustment description inconsistent.')
        self.assertTrue(b.getAdjustments()[1][1] == 'Adjustment 2', 'Adjustment description inconsistent.')

        self.assertTrue(b.getTotal() == 250, 'Adjustments should affect the bill total.')

        with self.assertRaises(ValueError):
            b.addAdjustment(-300, 'Try to make the bill negative.')

        self.assertTrue(b.getTotal() == 250, 'Failed adjustments should not be saved.')
        b.addAdjustment(-250, 'Zero out the bill.')

        self.assertTrue(b.getTotal() == 0, 'Adjustments should be allowed to zero-out the bill.')

    def test_getTotal(self):
        """
        Adjustments and charges should all affect the total.
        """
        b = Bill()

        b.charge = 100
        b.addAdjustment(350, 'Adjustment of 350')
        b.addAdjustment(-50, 'Adjustment of -50')

        self.assertTrue(b.getTotal() == 400, 'Adjustments and charges should be reflected by the bill total.')

        b.charge = 50

        self.assertTrue(b.getTotal() == 350, 'Adjustments and charges should be reflected by the bill total.')


    def test_charge(self):
        """
        A bill charge must be a positive integer.
        """
        b = Bill()

        b.charge = 20

        with self.assertRaises(TypeError):
            b.charge = None
        with self.assertRaises(TypeError):
            b.charge = 'abc'
        with self.assertRaises(TypeError):
            b.charge = 12.5

        with self.assertRaises(ValueError):
            b.charge = -40

        self.assertTrue(b.getTotal() == 20, 'Charge must not assume invalid values.')


        b.addAdjustment(-15, 'Bring bill down to 5.')
        self.assertTrue(b.getTotal() == 5, 'Negative adjustments should work.')

        with self.assertRaises(ValueError):
            b.charge = 10
        self.assertTrue(b.getTotal() == 5, 'Failed charge modification should not be saved.')

        b.charge = 15
        self.assertTrue(b.getTotal() == 0, 'Bill must be allowed to be zeroed-out via charge modification.')


class Tests_BillGroup(unittest.TestCase):
    """Tests the BillGroup object."""

    def test_init(self):
        """
        Test the Billgroup constructor.
        """
        g = BillGroup()

        self.assertTrue(len(g.getPayors()) == 0, 'No payors should be added yet.')
        self.assertTrue(g.getContributionTotal() == 0, 'No contributions should have been made yet.')

    def test_addOrUpdatePayor(self):
        """
        Payors should be added to the payor tuple array with their associated weight. A payor that already exists should
        be updated, not duplicated. When a payor is added or updated the liability for all payors should continue to
        calculate properly.
        """
        g = BillGroup()

        with self.assertRaises(TypeError):
            g.addOrUpdatePayor(None, 1)

        with self.assertRaises(TypeError):
            g.addOrUpdatePayor(1, None)
        with self.assertRaises(TypeError):
            g.addOrUpdatePayor(1, '')
        with self.assertRaises(ValueError):
            g.addOrUpdatePayor(1, -1)
        with self.assertRaises(ValueError):
            g.addOrUpdatePayor(1, 0)


        self.assertTrue(len(g.getPayors()) == 0, 'No payors should be added yet.')

        g.addOrUpdatePayor(1, 1)
        self.assertTrue(len(g.getPayors()) == 1, 'Payors should be able to be added to a shared bill.')
        self.assertTrue(g.calculateLiabilityFor(1) == 0, 'Payor liability should be able to be added to a shared bill.')

        g.addOrUpdatePayor(1, 4)

        self.assertTrue(len(g.getPayors()) == 1, 'Duplicate payors should not be created.')
        self.assertTrue(g.calculateLiabilityFor(1) == 0, 'Liability for a bill with zero contributions should be zero.')

        # With two payors, see if the liability changes correctly when we add a third.
        g.addOrUpdatePayor(2, 1)

        self.assertTrue(len(g.getPayors()) == 2, 'A second payor should have been added.')

        b1 = Bill()
        b1.charge = 500
        b1.addAdjustment(500, 'Adjustment')
        g.addBill(b1, 1)

        b2 = Bill()
        b2.charge = 200
        b2.addAdjustment(300, 'Adjustment')
        g.addBill(b2, 2)


        # At this point, payor 1 has paid in 1000 and payor 2 has paid in 500.
        # Payor 1 is responsible for 4/5 of the total bill, and payor 2 is responsible for 1/5.
        # Payor 1's liability should be (4/5) * 1500, less what they have already paid in.
        # So, 200.
        self.assertTrue(g.calculateLiabilityFor(1) == 200, 'Payor liability incorrect.')

        # Payor 2 is responsible for 300, but has paid in 500. They need to get back $200.
        self.assertTrue(g.calculateLiabilityFor(2) == -200, 'Payor liability incorrect.')

        # Now, a third payor joins, with no pay-in yet, and a weight of 5.
        g.addOrUpdatePayor(3, 5)

        self.assertTrue(g.calculateLiabilityFor(3) == 750, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(2) == -350, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(1) == -400, 'Payor liability incorrect.')

        # Now, they pay a bill, update their liability weight to 11 and a pay-in of $400.
        # Total of 1900, total liability weights of 16.

        b3 = Bill()
        b3.charge = 350
        b3.addAdjustment(25, 'Adjustment 1')
        b3.addAdjustment(15, 'Adjustment 2')
        b3.addAdjustment(45, 'Adjustment 3')
        b3.addAdjustment(-35, 'Adjustment 1')
        g.addBill(b3, 3)
        g.addOrUpdatePayor(3, 11)

        self.assertTrue(g.calculateLiabilityFor(1) == -525, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(2) == -381.25, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(3) == 906.25, 'Payor liability incorrect.')

        # Payor 1 pays a new bill.

        b11 = Bill()
        b11.charge = 150
        b1.addAdjustment(-50, 'Adjustment 1')
        g.addBill(b11, 1)

        # Total is now 2000.

        self.assertTrue(g.calculateLiabilityFor(1) == -600, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(2) == -375, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(3) == 975, 'Payor liability incorrect.')


    def test_getPayors(self):
        """
        Payors added to a bill are returned by getPayors.
        """
        g = BillGroup()

        self.assertTrue(len(g.getPayors()) == 0, 'No payors should be on a new bill group.')

        g.addOrUpdatePayor(1,1)
        g.addOrUpdatePayor(1,1)
        g.addOrUpdatePayor(2,1)
        g.addOrUpdatePayor(3,1)

        self.assertTrue(len(g.getPayors()) == 3, 'Payors were not added to the bill group.')
        self.assertTrue(set([1,2,3]) == set(g.getPayors()), 'Payors were not the same.')

    def test_removePayor(self):
        """
        Payors should be removable from the payor list and liability for everyone else should continue to calculate
        properly. A payor may not be removed if they have contributed to any bills, as this would prevent calculate
        liability from zeroing out.
        """
        g = BillGroup()
        g.addOrUpdatePayor(1, 40)
        g.addOrUpdatePayor(2, 60)

        with self.assertRaises(TypeError):
            g.removePayor(None)

        with self.assertRaises(ValueError):
            g.removePayor(400)

        self.assertTrue(g.calculateLiabilityFor(1) == 0, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(2) == 0, 'Payor liability incorrect.')

        b1 = Bill()
        b1.charge = 200
        g.addBill(b1, 1)

        # Total charge is 200.
        self.assertTrue(g.calculateLiabilityFor(1) == -120, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(2) == 120, 'Payor liability incorrect.')

        with self.assertRaises(ValueError):
            g.removePayor(1)

        self.assertTrue(g.calculateLiabilityFor(1) == -120, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(2) == 120, 'Payor liability incorrect.')

        g.removePayor(2)

        self.assertTrue(g.calculateLiabilityFor(1) == 0, 'Payor liability incorrect.')

        g.addOrUpdatePayor(2, 40)

        self.assertTrue(g.calculateLiabilityFor(1) == -100, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(2) == 100, 'Payor liability incorrect.')

    def test_addBill(self):
        """
        Adding a bill should adjust the liability of the payors. Should not be able to add a bill to a bill group that
        doesn't have the specified payor associated with the bill group already. Make sure we don't add the same bill
        twice.
        """
        g = BillGroup()

        b0 = Bill()
        b0.charge = 999

        with self.assertRaises(TypeError):
            g.addBill(b0, None)
        with self.assertRaises(ValueError):
            g.addBill(b0, 1)    # Can't add a bill to a non-existant payor.

        g.addOrUpdatePayor(1, 10)
        g.addOrUpdatePayor(2, 25)
        g.addOrUpdatePayor(3, 65)

        with self.assertRaises(TypeError):
            g.addBill(None, 1)
        with self.assertRaises(TypeError):
            g.addBill(400, 1)
        with self.assertRaises(TypeError):
            g.addBill('400', 1)

        self.assertTrue(g.calculateLiabilityFor(1) == 0, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(2) == 0, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(3) == 0, 'Payor liability incorrect.')

        b1 = Bill()
        b1.charge = 400
        g.addBill(b1, 1)
        b2 = Bill()
        b2.charge = 250
        g.addBill(b2, 2)

        with self.assertRaises(ValueError):
            g.addBill(b1)

        # Total charge is 650.
        self.assertTrue(g.calculateLiabilityFor(1) == -335, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(2) == -87.5, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(3) == 422.5, 'Payor liability incorrect.')


    def test_calculateLiabilityFor(self):
        """
        Liability for everyone should zero out. Liability should not calculate for non-existant payors.
        """
        g = BillGroup()

        with self.assertRaises(TypeError):
            g.calculateLiabilityFor(None)

        g.addOrUpdatePayor(1, 50)
        g.addOrUpdatePayor(2, 150)

        with self.assertRaises(ValueError):
            g.calculateLiabilityFor(4)

        b1 = Bill()
        b1.charge = 500
        g.addBill(b1, 1)

        b2 = Bill()
        b2.charge = 0
        b2.addAdjustment(750, 'Adjustment')
        g.addBill(b2, 2)

        self.assertTrue(g.calculateLiabilityFor(1) == -187.5, 'Payor liability incorrect.')
        self.assertTrue(g.calculateLiabilityFor(1) + g.calculateLiabilityFor(2) == 0, 'Liability sum did not zero out.')

    def test_getContributionFor(self):
        """
        Contributions for everyone should add up to the total contribution.
        :return:
        """
        g = BillGroup()

        with self.assertRaises(TypeError):
            g.getContributionFor(None)

        g.addOrUpdatePayor(1, 1)
        g.addOrUpdatePayor(2, 2)
        g.addOrUpdatePayor(3, 3)

        with self.assertRaises(ValueError):
            g.getContributionFor(4)

        self.assertTrue(g.getContributionFor(1) == 0, 'Contribution is wrong.')
        self.assertTrue(g.getContributionFor(2) == 0, 'Contribution is wrong.')
        self.assertTrue(g.getContributionFor(3) == 0, 'Contribution is wrong.')

        b1 = Bill()
        b1.charges = 20
        g.addBill(b1, 1)

        b2 = Bill()
        b2.charges = 15
        g.addBill(b2, 2)

        b3 = Bill()
        b3.charges = 10
        g.addBill(b3, 3)

        self.assertTrue(g.getContributionFor(1) == 20, 'Contribution is wrong.')
        self.assertTrue(g.getContributionFor(2) == 15, 'Contribution is wrong.')
        self.assertTrue(g.getContributionFor(3) == 10, 'Contribution is wrong.')

        self.assertTrue(g.getContributionTotal() == 45, 'Total contribution is wrong.')


    def test_getContributionTotal(self):
        """
        Calculates the total amount of the bills in this bill group.
        """
        g = BillGroup()

        self.assertTrue(g.getContributionTotal() == 0, 'Total contribution is wrong.')

        g.addOrUpdatePayor(1, 25)
        g.addOrUpdatePayor(2, 500)

        b1 = Bill()
        b1.charges = 20
        g.addBill(b1, 1)

        b2 = Bill()
        b2.charges = 5
        b2.addAdjustment(20, 'High')
        b2.addAdjustment(-10, 'Low')
        g.addBill(b2, 2)

        b3 = Bill()
        b3.charges = 10
        g.addBill(b3, 3)

        g.addBill(b1, 1)
        g.addBill(b2, 1)
        g.addBill(b3, 2)

        self.assertTrue(g.getContributionTotal() == 45, 'Total contribution is wrong.')