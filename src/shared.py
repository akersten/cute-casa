# ######################################################################################################################
# Shared Functionality
#
# Global features across the entire application.
# ######################################################################################################################

from flask import abort, session, g, request
import queries
from src import db
from src import enums
import src

def softstop():
    """
    Initiate a regular shutdown through the Werkzeug shutdown hook. Existing requests will continue to completion.
    Locks and database will shut down gracefully according to the after_request handler.
    """
    src.logger.logSystem('--- Soft Stop Initiated ---', enums.e_log_event_level.warning)

    if request is None:
        src.logger.logSystem('No request present, cannot soft stop.', enums.e_log_event_level.crash)

    k = request.environ.get('werkzeug.server.shutdown')
    if k is None:
        src.logger.logSystem('Not running within the Werkzeug server, cannot soft stop.', enums.e_log_event_level.crash)

    print('- Soft Stop -')
    k()

def hardstop():
    """
    Try to shutdown as cleanly as possible, saving databases and things.
    :return:
    """
    src.logger.logSystem('--- Hard Stop Initiated ---', enums.e_log_event_level.critical)

    if g is not None:
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()

    print('--- Hard Stop ---')
    raise SystemExit(0)

def checkLogin():
    """Check that the user is logged in and transmit an HTTP error if not."""
    if not session.get('logged_in'):
        abort(401)

def checkAdmin():
    """Check that the user is logged in as a CuteCasa admin."""
    checkLogin()
    if not session['admin']:
        abort(401, "you are not an admin")

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
    :param userId: THe user for which to get the households.
    :return: A list of households for the user.
    """
    return db.query_db(queries.USER_GET_HOUSEHOLDS, [userId,])

def setHousehold(householdId):
    """
    Set the current household for this session. Checks the validity of the household as well as the membership of the
    current user. Populates household session variables.
    :param householdId: The household id to switch to.
    :return: True if the household was successfully set, False otherwise.
    """
    # TODO: Check household validity.
    # TODO: Check household membership.
    checkLogin()

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
# Users
# ######################################################################################################################

def getUserRow(userId):
    """
    Get a user row based on their id.
    :param userId: The user id to look up.
    :return: The database row for this user.
    """
    user = db.getRow('users', userId)
    return user


def getUserDisplayname(userId):
    """
    Convert a user id into their display name.
    :param userId: The user id to look up.
    :return: The display name for this user.
    """
    name = db.getValue('users', 'displayname', userId)
    return name if name else 'System'


def isCuteCasaAdmin(userId):
    """
    Checks whether the given user is a CuteCasa administrator for this instance.
    :param userId: THe user id to check.
    :return: True if the specified user is a CuteCasa admin, False otherwise.
    """
    return db.getValue('users', 'e_user_authority', userId) == 2