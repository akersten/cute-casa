# ######################################################################################################################
# Shared Functionality
#
# Global features across the entire application.
# ######################################################################################################################

from flask import abort, session, g
import queries
from src import db

def checkLogin():
    """Check that the user is logged in and transmit an HTTP error if not."""
    if not session.get('logged_in'):
        abort(401)


def getHouseholdType(householdId):
    return db.getSingleValue("households", "e_household_type", householdId)