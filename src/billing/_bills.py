import persistent, transaction

class Bill(persistent.Persistent):
    """
    A Bill represents a single charge. It might be a utility bill, or a grocery bill (with many line items).
    Bills have the following:
        * Charge - dollar amount needed to pay this bill.
        * Adjustments - dollar amount discounts or additions to this bill (e.g. in a shared bill, one might deduct a few
                        line items for personal purchases in the context of a larger grocery bill). A landlord might be
                        generous and offer a discount on a utility bill for a holiday. Or they might be mean and add a
                        positive adjustment.
        * Total - dollar amount of charges less the sum of deductions, always positive. A bill can never be adjusted to
                  have a negative total.
    """

    def __init__(self):
        self._charge = 0    # Initialize private member first before running the property setter, since the setter looks
                            # to this parameter for a value check.

        self._adjustments = []
        self.charge = 0

    def addAdjustment(self, amount, why):
        if amount is None or type(amount) is not int:
            raise TypeError('Amount must be an integer.')
        if self.getTotal() + amount < 0:
            raise ValueError('An adjustment may not cause the bill amount to become negative.')


        self._adjustments.append((amount, why))

    def getAdjustments(self):
        """
        Return the adjustments on this bill.
        :return: The adjustments applied to this bill as an array of tuples: (amount, why).
        """
        return self._adjustments


    def getTotal(self):
        """
        Recalculate the total for this bill.
        """
        adjustments = sum(i for i, __ in self._adjustments)
        return self.charge + adjustments

    @property
    def charge(self):
        return self._charge

    @charge.setter
    def charge(self, value):
        if value is None or type(value) is not int:
            raise TypeError('Charge must be an integer.')
        if value < 0:
            raise ValueError('Charge must be non-negative.')

        if (self.getTotal() - self.charge) + value < 0:
            raise ValueError('New charge may not cause the bill amount to become negative.')

        self._charge = value
        transaction.commit()




class BillGroup(persistent.Persistent):
    """
    A bill group is a group of Bills whose liability is split between multiple payors. Whenever a new bill is added, the
    assumption is that a payor has already paid the bill, and that the amount of the bill is their "contribution" to the
    shared pot of money, which will be redistributed according to the split of everyone in the shared bill group.
    """

    def __init__(self):
        self._bills = []
        self._payors = []

    def addOrUpdatePayor(self, payor, weight):
        """
        Adds or updates a payor on this bill.
        :param payor: The id of the payor.
        :param weight: The weight relative to other payor weights that this payor is responsible for.
        """

        transaction.commit()

    def removePayor(self, payor):

        transaction.commit()

    def addBill(self, payor):
        """
        Adds a bill to this bill group with the associated payor.
        :param payor: The user id of who paid this bill.
        """
        pass

    def calculateLiabilityFor(self, who):
        """
        Calculates the liability for this bill
        :param who:
        :param splitMap:
        :return:
        """
        pass

    def getContributionFor(self, who):
        """
        Calculates how much someone in particular has contributed to the bills.
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