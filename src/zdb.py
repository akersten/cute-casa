# ######################################################################################################################
# Object Database functionality
#
# ######################################################################################################################

import ZODB, ZODB.FileStorage, BTrees.OOBTree, transaction
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
        logger.logSystem("Schema creation invoked without a database.", enums.e_log_event_level.crash)
    if root is None:
        logger.logSystem("Schema creation invoked without a root element.", enums.e_log_event_level.crash)


    if not hasattr(root, 'globalSettings'):
        logger.logSystem('Creating default global settings.')
        #TODO
    else:
        logger.logSystem('Using existing global settings.')
        #TODO


    if not hasattr(root, 'households'):
        logger.logSystem('Creating household collection...')
        root.households = BTrees.OOBTree.BTree()
    else:
        logger.logSystem('Household collection exists, it is: ' + root.households)

    transaction.commit()



def getHousehold(householdId):
    """
    Get a household from the database.
    :param householdId: The household id to retrieve.
    :return: A household object corresponding to this id.
    """

def createHousehold(householdId):
    """
    Create a household and add it to the database.
    :param householdId: The household to create.
    :return: A handle to the household.
    """
