from flask import flash, render_template, request, session, g, redirect, url_for

from src import shared
from src import db
from src import logger
from src import enums
import queries


def dashboard():
    """
    The admin dashboard has links to other admin pages. Render the dashboard view.
    :return: The render template.
    """
    logger.logAdmin("Admin dashboard accessed.", session['id'], enums.e_log_event_level.warning)
    return render_template('admin/dashboard.html')


def logviewer(logname, after):
    """
    The admin log viewer shows administrative events. Render the logviewer.
    :return: The render template.
    """
    logger.logAdmin("Logviewer accessed.", session['id'], enums.e_log_event_level.warning)
    return render_template('admin/logviewer.html', events=getEvents(logname, after, 50), getUserDisplayname=lambda n: shared.getUserDisplayname(n))

def getEvents(logname, after, count):
    """
    Return the events after a certain index.
    :param after: Index to start events (descending)
    :param count: How many events to pull.
    :return: An array of events.
    """
    if logname == "system":
        return db.query_db(queries.SYSTEM_LOG_GET, [after, count])
    elif logname == "admin":
        return db.query_db(queries.ADMIN_LOG_GET, [after, count])
    else:
        return None