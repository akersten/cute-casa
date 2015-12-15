from flask import flash, render_template, session, abort

from src import logger
from src import enums
from src import shared

def billsplit():
    """
    Certain bills associated with a household are running tallies resolved at the end of each month (like a grocery
    bill). This is a tool to split them between members of a household.
    Render the billsplit view.
    :return: The render template.
    """
    return render_template('billing/billsplit.html')

def dashboard():
    """
    Render the billing dashboard.
    :return: The render template.
    """
    return render_template('billing/dashboard.html');

def admin():
    """
    Render the admin dashboard.
    :return: The render template.
    """
    if not session.get('householdId'):
        abort(400, "householdId missing")

    if not shared.getHouseholdRelation(session['householdId'], session['id']) == enums.e_household_relation.admin:
        abort(403, 'not authorized as an admin for this household')

    return render_template('billing/admin.html')

def billboard():
    """
    Return the billboard, the view of all the bills that contribute to a household invoice.
    :return:
    """

    return render_template('billing/billboard.html')