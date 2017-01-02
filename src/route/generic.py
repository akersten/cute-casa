# ######################################################################################################################
# Generic top-level routes like the splash screen and main dashboard.
# ######################################################################################################################

from flask import session, redirect, url_for, render_template

from core.household import household


def splash():
    """
    The splash screen for the CuteCasa homepage - redirects to the dashboard if the user is logged in.
    :return: The rendered template.
    """
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return render_template("splash.html")


def dashboard():
    """
    The landing page for a logged in user.
    :return: The rendered template.
    """
    if not session.get('householdId'):
        return redirect(url_for('household_select'))
    return render_template('dashboard.html', members=household.getUsersForHousehold(session['householdId']))
