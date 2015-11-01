# ######################################################################################################################
# Shared Functionality
#
# Global features across the entire application.
# ######################################################################################################################
from flask import abort, session


def checkLogin():
    """Check that the user is logged in and transmit an HTTP error if not."""
    if not session.get('logged_in'):
        abort(401)
