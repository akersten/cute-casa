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


class Tests_BillGroup(unittest.TestCase):
    """Tests the BillGroup object."""

    def test_init(self):
        """
        Billgroup constructor.
        """
        pass


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