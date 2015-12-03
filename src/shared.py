# ######################################################################################################################
# Shared Functionality
#
# Global features across the entire application.
# ######################################################################################################################

from flask import abort, session
import queries
from src import db

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
    return name if name else 'unknown user'


def isCuteCasaAdmin(userId):
    """
    Checks whether the given user is a CuteCasa administrator for this instance.
    :param userId: THe user id to check.
    :return: True if the specified user is a CuteCasa admin, False otherwise.
    """
    return db.getValue('users', 'e_user_authority', userId) == 2