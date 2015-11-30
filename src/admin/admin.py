from flask import flash, render_template, request, session, g, redirect, url_for
import queries


def dashboard():
    """
    The admin dashboard has links to other admin pages. Render the dashboard view.
    :return: The render template.
    """
    return render_template('admin/dashboard.html')


def logviewer():
    """
    The admin log viewer shows administrative events. Render the logviewer.
    :return: The render template.
    """
    return render_template('admin/logviewer.html')