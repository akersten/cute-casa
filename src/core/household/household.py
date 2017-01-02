from core.user import user
from core.database import db, queries

from flask import session


def getHouseholdType(householdId):
    """
    Returns the household type for a given household.
    :param householdId: The household to check.
    :return: The type of this household (from enums.e_household_type).
    """
    return db.getValue("households", "e_household_type", householdId)

def getHouseholdRelation(householdId, userId):
    """
    Returns the relation between this household and this user.
    :param householdId: The household to check.
    :param userId: The user to check.
    :return: A relation from enums.e_household_relation.
    """
    val = db.query_db(queries.HOUSEHOLD_MEMBERSHIP_GET_FOR_USER_AND_HOUSEHOLD, [userId, householdId], True)
    return val['e_household_relation'] if val is not None else None

def getHouseholdsForUser(userId):
    """
    Returns a list of households for a given user. Keys in each dictionary within the returned list are:
        * households.id
        * households.household_name
        * households.e_household_type
        * household_memberships.e_household_relation
    :param userId: The user for which to get the households.
    :return: A list of households for the user.
    """
    return db.query_db(queries.USER_GET_HOUSEHOLDS_NO_REQUESTS, [userId, ])

def getUsersForHousehold(householdId):
    """
    Returns a list of users for a given household. Keys in each dictionary within the returned list are:
        * id
        * membership_date
        * e_household_relation
    :param householdId:
    :return: A list of users for the household.
    """
    return db.query_db(queries.HOUSEHOLD_GET_USERS, [householdId, ])

def getUsersForCurrentHousehold():
    """
    Returns a list of users for the currently selected household.
    :return: A list of users for the currently selected household.
    """
    return getUsersForHousehold(session["householdId"])

def setHousehold(householdId):
    """
    Set the current household for this session. Checks the validity of the household as well as the membership of the
    current user. Populates household session variables.
    :param householdId: The household id to switch to.
    :return: True if the household was successfully set, False otherwise.
    """
    # TODO: Check household validity.
    # TODO: Check household membership.
    user.checkLogin()

    house = db.getRow('households', householdId)
    if house is None:
        return False

    session['householdId'] = house['id']
    session['householdName'] = house['household_name']
    session['householdType'] = house['e_household_type']
    session['householdRelation'] = getHouseholdRelation(house['id'], session['id'])
    return True

def unsetHousehold():
    """
    Erase the current household data from the session, like when we go back to the household select screen.
    """
    session.pop('householdId')
    session.pop('householdName')
    session.pop('householdType')
    session.pop('householdRelation')



# ######################################################################################################################
# Household object representation
# ######################################################################################################################

import persistent, transaction
from core.household.shopping import ShoppingList

class Household(persistent.Persistent):

    def __init__(self, householdId):
        if not type(householdId) is str:
            raise TypeError('A household id must be of str type.')

        if len(householdId) == 0:
            raise ValueError('A household id must be non-zero length.')

        # SQL properties
        self.householdId = householdId

        # Object properties
        self._members = []
        self._sharedBills = []
        self._shoppingLists = []

    def addMember(self, member):
        pass


    def getSharedBills(self):
        """
        Gets the shared bills for this household, along with each's index in the shared bills list.
        :return: Tuple (idx, SharedBill) for each shared bill in the household.
        """
        return enumerate(self._sharedBills)

    def getShoppingLists(self):
        """
        Gets the shopping lists for this household, along with each's index in the shopping lists list.
        :return: Tuple (idx, ShoppingList) for each shopping list in the household.
        """
        return enumerate(self._shoppingLists)

    def addShoppingList(self, shoppingListTitle):
        self._shoppingLists.append(ShoppingList(shoppingListTitle))
        self._p_changed = True
        transaction.commit()