import hashlib

from flask import session, redirect, url_for, render_template, abort, request, flash, Flask

from core import logger
from core.database import db, queries
from core.user import user

import route.admin
import route.billing
import route.household
import route.user

from route.admin import admin
from route.billing import billing
from route.household import household


def init_routes(flask_app: Flask) -> None:
    """
    Sets up the application routes on the Flask object by looking into each area's package __init__.py and running its
    route initialization.
    :param flask_app: The Flask application.
    """
    flask_app.add_url_rule('/', 'splash', view_func=lambda: generic_endpoint("splash"))


    route.admin.init_routes(flask_app)
    route.billing.init_routes(flask_app)
    route.household.init_routes(flask_app)
    route.user.init_routes(flask_app)


def generic_endpoint(endpoint):
    """
    Based on the URL, determine which view to render a template for. This should be used for endpoints that don't
    require much special logic (e.g. the splash screen).
    :param endpoint: The endpoint to render.
    :return: The rendered template.
    """
    template = ""

    if endpoint=="splash":
        if (session.get("logged_in")):
            return redirect(url_for("dashboard"))
        template="splash.html"

    return render_template(template)



# TODO:  Clean up the below?



# noinspection PyUnresolvedReferences
#@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """
    Render the dashboard view. This will be the home screen that everyone sees upon logging in.
    :return: The render template.
    """
    user.checkLogin()
    if not session.get('householdId'):
        return redirect(url_for('household_select'))
    return render_template('dashboard.html', members=household.getUsersForHousehold(session['householdId']))

# ######################################################################################################################
#   User profile and actions.
# ######################################################################################################################

# noinspection PyUnresolvedReferences
#@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    user.checkLogin()
    return user.profile()

# ######################################################################################################################
#   Household profile and actions.
# ######################################################################################################################

# noinspection PyUnresolvedReferences
#@app.route('/household/select/', methods=['GET'])
#@app.route('/household/select/<householdId>', methods=['GET'])
def household_select(householdId=None):
    user.checkLogin()
    return household.select(householdId)

# noinspection PyUnresolvedReferences
#@app.route('/household/profile', methods=['GET', 'POST'])
def household_profile():
    user.checkLogin()
    return household.profile()

# noinspection PyUnresolvedReferences
#@app.route('/household/search/<partial>', methods=['GET'])
def household_search(partial):
    user.checkLogin()
    return household.search(partial)

# noinspection PyUnresolvedReferences
#@app.route('/household/request/<id>')
def household_request(id):
    user.checkLogin()
    return household.household_request(id)

# noinspection PyUnresolvedReferences
#@app.route('/household/approve/<householdId>/<id>')
def household_approve(householdId, id):
    user.checkLogin()
    return household.household_approve(householdId, id)

# noinspection PyUnresolvedReferences
#@app.route('/household/deny/<householdId>/<id>')
def household_deny(householdId, id):
    user.checkLogin()
    return household.household_deny(householdId, id)

# ######################################################################################################################
#   Billing actions.
# ######################################################################################################################

# noinspection PyUnresolvedReferences
#@app.route('/billing/dashboard', methods=['GET'])
def billing_dashboard():
    user.checkLogin()
    return billing.dashboard()

# noinspection PyUnresolvedReferences
#@app.route('/billing/admin', methods=['GET'])
def billing_admin():
    user.checkLogin()
    return billing.admin()

# noinspection PyUnresolvedReferences
#@app.route('/billing/billsplit', methods=['GET', 'POST'])
def billing_billsplit():
    user.checkLogin()
    return billing.billsplit()

# noinspection PyUnresolvedReferences
#@app.route('/billing/billsplit/create', methods=['POST'])
def billing_billsplit_create():
    user.checkLogin()
    return billing.billsplit_create()

# noinspection PyUnresolvedReferences
#@app.route('/billing/utilities', methods=['GET'])
def billing_utilities():
    user.checkLogin()
    return billing.utilities()

# ######################################################################################################################
# Admin actions.
# ######################################################################################################################

# noinspection PyUnresolvedReferences
#@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    user.checkAdmin()
    return admin.dashboard()

# noinspection PyUnresolvedReferences
#@app.route('/admin/logviewer/<logname>/<after>', methods=['GET'])
def admin_logviewer(logname, after):
    user.checkAdmin()
    return admin.logviewer(logname, after)

# noinspection PyUnresolvedReferences
#@app.route('/admin/nodeviewer/<node>', methods=['GET'], defaults={'index': None})
#@app.route('/admin/nodeviewer/<node>/<index>', methods=['GET'])
def admin_nodeviewer(node, index):
    user.checkAdmin()
    return admin.nodeviewer(node, index)

# noinspection PyUnresolvedReferences
#@app.route('/admin/styletest', methods=['GET'])
def admin_styletest():
    user.checkAdmin()
    return admin.styletest()

# noinspection PyUnresolvedReferences
#@app.route('/admin/globalSettings', methods=['GET', 'POST'])
def admin_globalSettings():
    user.checkAdmin()
    return admin.globalSettings()
