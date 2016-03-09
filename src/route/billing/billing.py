from flask import flash, render_template, session, abort, redirect, url_for

from src.core import enums, shared


def billsplit():
    """
    Certain bills associated with a household are running tallies resolved at the end of each month (like a grocery
    bill). This is a tool to split them between members of a household.
    Render the billsplit view.
    :return: The render template.
    """
    return render_template('billing/billsplit.html')

def utilities():
    """
    Utilities are shared between household members at certain percentage responsibilities per member.
    :return: The render template.
    """
    return render_template('billing/utilities.html')

def dashboard():
    """
    Render the billing dashboard.
    :return: The render template.
    """
    return render_template('billing/dashboard.html')

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


def billsplit_create():
    """
    The async call when creating a new split bill.
    """
    flash('Shared bill created.', 'info')
    return redirect(url_for('billing_billsplit'))