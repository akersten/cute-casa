# ######################################################################################################################
# Object Database functionality
#
# ######################################################################################################################

import ZODB, ZODB.FileStorage, BTrees.OOBTree, transaction



from src import logger
from src import enums

from src.household.household import Household
from src._shared.globalSettings import GlobalSettings


class DuplicateRecordException(Exception):
    """Exception raised when attempting to create a duplicate record inside one of the ZDB b-trees."""
    pass

# The zdb database reference and root element..
class Zdb():

    def __init__(self, dbPath):
        self.zdb = None
        self.root = None
        self.bringup(dbPath)

    def bringup(self, dbPath):
        """
        Initialize the object database.
        :return:
        """
        logger.logSystem("Bringing up ZODB...")

        storage = ZODB.FileStorage.FileStorage(dbPath) # usually 'secret/cute.zdb'
        self.zdb = ZODB.DB(storage)
        connection = self.zdb.open()
        self.root = connection.root

        self.schemaCheckAndCreate()

        logger.logSystem("... ZODB bringup finished.")


    def teardown(self):
        if not self.zdb is None:
            self.zdb.close()


    def schemaCheckAndCreate(self):
        """
        Checks the root object for the presence of the expected BTrees and creates them if they do not exist.
        """
        if self.zdb is None:
            logger.logSystem("Schema creation invoked without a database.", enums.e_log_event_level.crash)
        if self.root is None:
            logger.logSystem("Schema creation invoked without a root element.", enums.e_log_event_level.crash)


        if not hasattr(self.root, 'globalSettings'):
            logger.logSystem('Creating default global settings...')
            self.root.globalSettings = GlobalSettings()

        if not hasattr(self.root, 'households'):
            logger.logSystem('Creating household collection...')
            self.root.households = BTrees.OOBTree.BTree()

        transaction.commit()



    def getHousehold(self, householdId):
        """
        Get a household from the database.
        :param householdId: The household id to retrieve.
        :return: A household object corresponding to this id.
        """
        if householdId is None:
            return None

        try:
            return self.root.households[householdId]
        except KeyError:
            return None

    def createHousehold(self, householdId):
        """
        Create a household and add it to the database.
        :param householdId: The household to create. A string id for the household.
        :return: A handle to the household.
        """
        if not type(householdId) is str:
            raise ValueError('A household id must be of str type.')

        if len(householdId) == 0:
            raise ValueError('A household id must be non-zero length.')

        if householdId in self.root.households:
            raise DuplicateRecordException("A household with this id already exists.")

        house = Household(householdId)
        self.root.households[householdId] = house
        return house

