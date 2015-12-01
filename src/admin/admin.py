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
    logger.logAdmin(session['id'], enums.e_admin_log_event_level.warning, "Admin dashboard accessed.")
    return render_template('admin/dashboard.html')


def logviewer(after):
    """
    The admin log viewer shows administrative events. Render the logviewer.
    :return: The render template.
    """
    logger.logAdmin(session['id'], enums.e_admin_log_event_level.warning, "Logviewer accessed.")
    return render_template('admin/logviewer.html', events=getEvents(after, 50), id2displayname=lambda n: shared.id2displayname(n))

def getEvents(after, count):
    """
    Return the events after a certain index.
    :param after: Index to start events (descending)
    :param count: How many events to pull.
    :return: An array of events.
    """
    return db.query_db(queries.ADMIN_LOG_GET, [after, count])