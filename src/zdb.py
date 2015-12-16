# ######################################################################################################################
# Object Database functionality
#
# ######################################################################################################################

import ZODB, ZODB.FileStorage, BTrees
from src.household import household

from src import logger
from src import enums

def init():
    """
    Initialize the object database.
    :return:
    """
    print("WTF")

    storage = ZODB.FileStorage.FileStorage('secret/cute.zdb')
    db = ZODB.DB(storage)
    connection = db.open()
    root = connection.root


    if not hasattr(root, 'households'):
        print("Creating BTree for Households...")
        root.households = "yes"
    else:
        print("Root households is " + root.households)


def getHousehold(householdId):
    """
    Get a household from the database.
    :param householdId:
    :return:
    """


def createHousehold(householdId, householdName, householdType):
    """
    Create a household and add it to the database.
    :param householdId:
    :param householdName:
    :param householdType:
    :return:
    """
