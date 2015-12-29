# ######################################################################################################################
# Object Database functionality
#
# ######################################################################################################################

import ZODB, ZODB.FileStorage, BTrees.OOBTree, transaction
from src.household import household

from src import logger
from src import enums


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
        connection = zdb.open()
        self.root = connection.root

        self.schemaCheckAndCreate()


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
            logger.logSystem('Creating default global settings.')
            #TODO
        else:
            logger.logSystem('Using existing global settings.')
            #TODO


        if not hasattr(self.root, 'households'):
            logger.logSystem('Creating household collection...')
            self.root.households = BTrees.OOBTree.BTree()
        else:
            logger.logSystem('Household collection exists, it is: ' + self.root.households)

        transaction.commit()



    def getHousehold(self, householdId):
        """
        Get a household from the database.
        :param householdId: The household id to retrieve.
        :return: A household object corresponding to this id.
        """

    def createHousehold(self, householdId):
        """
        Create a household and add it to the database.
        :param householdId: The household to create.
        :return: A handle to the household.
        """
