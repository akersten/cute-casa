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
    return db.getSingleValue("households", "e_household_type", householdId)

def isCuteCasaAdmin(userId):
    return db.getSingleValue('users', 'e_user_authority', userId) == 2

def id2displayname(userId):
    """
    Convert a user id into their display name.
    :param userId: The user id to look up.
    :return: The display name for this user.
    """
    name = db.getSingleValue('users', 'displayname', userId)
    return name if name else 'unknown user'