from flask import request, redirect, url_for

from core import enums, logger


# Convenience methods to do things to the client request, like send a failure page, or format ajax json.


def failRequest(code, message):
    """
    Aborts a Flask request with the specified error code and message. Logs the event to the user log.
    :param code: The HTTP code to which this failure corresponds.
    :param message: The problem with the request.
    :return: A redirect to an error page.
    """
    if not enums.contains(enums.e_http_codes, code):
        failRequest(enums.e_http_codes.internal_error, 'Invalid HTTP code specified while processing another error.')

    logger.logUser()
    if request.method == 'POST':
        # Can't redirect to the error page - it was an Ajax request! Send some error JSON instead.
        pass
    else:
        return redirect(url_for(message))


def run_integrity_checks():

    # TODO: We need to just force a logout here since the user probably doesn't exit
    # TODO: Don't populate these items, have a cleaner API for getting useful items.

    # Populate useful items
    if 'id' in session:
        g.dog.me = g.dog.zdb.getUser(session['id'])

        if g.dog.me is None:
            logger.logSystem('Integrity error - user object lookup failed for user id ' + str(session['id']),
                             enums.e_log_event_level.critical)
            session.clear()
            flash('Please log in again.', 'info')
            return redirect(url_for('splash'))

    if 'householdId' in session:
        g.dog.hh = g.dog.zdb.getHousehold(session['householdId'])

        if g.dog.hh is None:
            logger.logSystem("Integrity error - household object lookup failed for household id " +
                             str(session['householdId']),
                             enums.e_log_event_level.critical)
            session.clear()
            flash('Please log in again.', 'info')
            return redirect(url_for('splash'))