import persistent, transaction, datetime

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
        self._charge = 0
        self._owner = None
        self._name = None
        self._date = None
        self._active = True
        transaction.commit()

    def addAdjustment(self, amount, why):
        if amount is None or type(amount) is not int:
            raise TypeError('Amount must be an integer.')
        if self.getTotal() + amount < 0:
            raise ValueError('An adjustment may not cause the bill amount to become negative.')


        self._adjustments.append((amount, why))
        self._p_changed = True
        transaction.commit()

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

    @property
    def name(self):
        """The title of this bill."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        transaction.commit()

    @property
    def owner(self):
        """A bill can have an associated owner."""
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value
        transaction.commit()

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if type(value) is not datetime.datetime:
            raise TypeError('A date must be of type datetime.')

        self._date = value
        transaction.commit()

    @property
    def active(self):
        """
        Whether this bill is active or not. The interpretation of active depends on what type of bill this is.
            * If this bill is part of a shared bill, active indicates that this bill is part of a cycle that has not
            been finalized yet.
        """
        return self._active

    @active.setter
    def active(self, value):
        if type(value) is not bool:
            raise TypeError('Active must be either true or false.')

        self._active = value
        transaction.commit()


class BillGroup(persistent.Persistent):
    """
    A bill group is a group of Bills whose liability is split between multiple payors. Whenever a new bill is added, the
    assumption is that a payor has already paid the bill, and that the amount of the bill is their "contribution" to the
    shared pot of money, which will be redistributed according to the split of everyone in the shared bill group.

    Bill groups are tracked in cycles, which are buckets of bills split by e.g. month.
    """

    def __init__(self):
        self._bills = []    # List of bills with owners.
        self._payors = {}   # Tuple of payor => weight
        self._name = None

    def addOrUpdatePayor(self, payor, weight):
        """
        Adds or updates a payor on this bill.
        :param payor: The id of the payor.
        :param weight: The weight relative to other payor weights that this payor is responsible for. Must be positive.
        :raises TypeError: If payor is None or weight is not an integer.
        :raises ValueError: If weight is negative.
        """
        if payor is None:
            raise TypeError('Payor must not be None.')
        if weight is None or not type(weight) is int:
            raise TypeError('Weight must be an integer.')
        if weight <= 0:
            raise ValueError('Weight must be positive.')

        self._payors[payor] = weight
        self._p_changed = True
        transaction.commit()

    def removePayor(self, payor):
        """
        Removes a payor from the shared bill. Cannot remove a payor if they have bill contributions on this shared bill.
        :param payor: The payor to remove from this shared bill.
        :raises TypeError: If None is passed as the payor.
        :raises ValueError: The payor does not exist on this bill, or cannot be removed due to having payments.
        """
        if payor is None:
            raise TypeError('A payor must be specified.')

        if not payor in self.getPayors():
            raise ValueError('This payor does not exist for this bill.')

        count = len([bill for bill in self._bills if bill.owner == payor])
        if (count > 0):
            raise ValueError('A payor cannot be removed if they have bills associated with them.')

        self._payors.pop(payor)
        self._p_changed = True
        transaction.commit()

    def getPayors(self):
        """
        Returns a list of payors on this shared bill.
        :return: A list of payors on this shared bill.
        """
        return self._payors.keys()

    def addBill(self, bill, payor):
        """
        Adds a bill to this bill group with the associated payor.
        :param bill: The bill to add.
        :param payor: The user id of who paid this bill.
        :raise TypeError: If a Bill type wasn't passed as the bill, or None was passed as a parameter.
        :raise ValueError: If the bill has already been added.
        """
        if type(bill) is not Bill:
            raise TypeError('Can only add bills.')
        if payor is None:
            raise TypeError('A bill must have a payor.')

        if bill in self._bills:
            raise ValueError('This bill is already part of this shared bill.')
        if payor not in self.getPayors():
            raise ValueError('This payor is not associated with this bill group.')

        bill.owner = payor
        self._bills.append(bill)
        self._p_changed = True
        transaction.commit()

    def calculateLiabilityFor(self, who):
        """
        Calculates the liability for this bill. If positive, this payor needs to pay that much more into the pot.
        If negative, this person needs to be paid out from the pot.
        :param who:
        :param splitMap:
        :return:
        """
        if who is None:
            raise TypeError('Cannot calculate liability for None.')
        if who not in self.getPayors():
            raise ValueError('This payor is not associated with this bill group.')

        if self._getWeightSum() == 0:
            return 0

        myResponsibility = (self._payors[who] / self._getWeightSum()) * self.getContributionTotal()
        myContribution = self.getContributionFor(who)
        return myResponsibility - myContribution

    def _getWeightSum(self):
        """
        Gets the sum of the liability weights for this group bill.
        :return: The sum of the liability weights for this group bill.
        """
        return sum(self._payors.values())

    def getContributionFor(self, who):
        """
        Calculates how much someone in particular has contributed to the bills.
        :param who: The payor.
        :return: A sum of how much this payor has paid towards this shared bill.
        """
        if who is None:
            raise TypeError('Cannot calculate contribution for None.')
        if who not in self.getPayors():
            raise ValueError('This payor is not associated with this bill group.')

        return sum([b.getTotal() for b in self._bills if b.owner == who])

    def getContributionTotal(self):
        """
        Calculates the total amount of the bills in this bill group.
        :return: The total dollar amount of bills in the bill group.
        """
        return sum([b.getTotal() for b in self._bills])

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        transaction.commit()