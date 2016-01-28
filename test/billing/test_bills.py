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

        b.charge = -200

        self.assertTrue(b.getTotal() == 100, 'Adjustments and charges should be reflected by the bill total.')


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
        Billgroup constructor.
        """
        pass

    def helper_setup(self, bg, people):
        """
        Helper function to add bills to a bill group. Odd people will get 1 bill, even people will get 2 bills. The
        liability will be the integer weight of the index of the person. Even people's bills will be 100, odd will be
        175.
        :param bg: The bill group to add to.
        :param people: The number of people to add bills for.
        :return:
        """

        for x in range(1, people):
            bg.addOrUpdatePayor(x, x)
            b1 = Bill()
            b1.charge = 200
            b1.addAdjustment(-100, 'Adjustment 1')
            bg.addBill(b1, x)
            if x % 2 == 0:
                b2 = Bill()
                b2.charge = 50
                b2.addAdjustment(25, 'Adjustment 2')
                bg.addBill(b2, x)


    def test_addOrUpdatePayor(self):
        """
        Payors should be added to the payor tuple array with their associated weight. A payor that already exists should
        be updated, not duplicated. When a payor is added or updated, the liability for all payors should continue to
        calculate properly.
        """
        g = BillGroup()



        pass

    def test_removePayor(self):
        """
        Payors should be removable from the payor list and liability for everyone else should continue to calculate
        properly. A payor may not be removed if they have contributed to any bills, as this would prevent calculate
        liability from zeroing out.
        """

        pass

    def test_addBill(self):
        """
        Adding a bill should adjust the liability of the payors.
        """
        pass

    def test_calculateLiabilityFor(self):
        """
        Liability for everyone should zero out.
        """
        pass

    def getContributionFor(self, who):
        """
        Contributions for everyone should add up to the total contribution.
        :param who:
        :return:
        """
        pass

    def getContributionTotal(self):
        """
        Calculates the total amount of the bills in this bill group.
        :return: The total dollar amount of bills in the bill group.
        """
        pass