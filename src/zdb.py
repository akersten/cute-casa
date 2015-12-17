# ######################################################################################################################
# Object Database functionality
#
# ######################################################################################################################

import ZODB, ZODB.FileStorage, BTrees
from src.household import household

from src import logger
from src import enums


# The zdb database reference and root element..
zdb = None
root = None

def bringup():
    global zdb, root

    """
    Initialize the object database.
    :return:
    """
    logger.logSystem("Bringing up ZODB...")

    storage = ZODB.FileStorage.FileStorage('secret/cute.zdb')
    zdb = ZODB.DB(storage)
    connection = zdb.open()
    root = connection.root

    schemaCheckAndCreate()
    if not hasattr(root, 'households'):
        logger.logSystem("")
        root.households = "yes"
    else:
        print("Root households is " + root.households)


def teardown():
    global zdb

    if not zdb is None:
        zdb.close()


def schemaCheckAndCreate():
    """
    Checks the root object for the presence of the expected BTrees and creates them if they do not exist.
    """
    global zdb, root

    if zdb is None:
        logger.logSystem("Schema creation invoked without a database.", enums.e_system_log_event_level.crash)
    if root is None:
        logger.logSystem("Schema creation invoked without a root element.", enums.e_system_log_event_level.crash)

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
