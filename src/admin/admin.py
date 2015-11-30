from flask import flash, render_template, request, session, g, redirect, url_for

from src import db
import queries


def dashboard():
    """
    The admin dashboard has links to other admin pages. Render the dashboard view.
    :return: The render template.
    """
    return render_template('admin/dashboard.html')


def logviewer(after):
    """
    The admin log viewer shows administrative events. Render the logviewer.
    :return: The render template.
    """

    return render_template('admin/logviewer.html', events=getEvents(after, 50))

def getEvents(after, count):
    """
    Return the events after a certain index.
    :param after: Index to start events (descending)
    :param count: How many events to pull.
    :return: An array of events.
    """
    return db.query_db(queries.ADMIN_LOG_GET, [after, count])