# ######################################################################################################################
# The application entry point. Run this via cute.sh so that environment variables are set.
# ######################################################################################################################

import sqlite3
from contextlib import closing
import os
import hashlib

from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash


from src import shared
from src import db
from src import zdb
from src import logger
from src import enums
from src.user import user
from src.household import household
from src.billing import billing
from src.admin import admin

from src._notification.yo.yoer import Yoer

import queries

VERSION = "0.0.0"

# Read configuration from environment variables - these are set by the secret script that we don't commit...
DATABASE = os.environ.get('CUTE_DB')
DEBUG = (os.environ.get('CUTE_DEBUG') in ['True', 'true', '1', 'yes']) or True
SECRET_KEY = os.environ.get('CUTE_SECRET_KEY')
USERNAME = os.environ.get('CUTE_USERNAME')
PASSWORD = os.environ.get('CUTE_PASSWORD')
PORT = os.environ.get('CUTE_PORT')
SALT = os.environ.get('CUTE_SALT')


# Singletons

S_Zdb = None
S_Yoer = None

def notSet(problem):
    """
    Abort initialization if any of the configuration environment variables isn't set.
    :param problem: The item that is not set.
    """
    print(problem + " not set! Run through the secret shell script.")
    exit(1)


if USERNAME is None:
    notSet("Username")

if PASSWORD is None:
    notSet("Password")

if SECRET_KEY is None:
    notSet("Secret key")

if SALT is None:
    notSet("Salt")

if PORT is None:
    notSet("Port")

PORT = int(PORT)

print("Starting CuteCasa backend " + VERSION + "...")

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


# Bringup and teardown
@app.before_request
def before_request():
    g.db = connect_db()

    # Add singleton references to dog object.
    g.dog = lambda: None
    g.dog.zdb = S_Zdb
    g.dog.yoer = S_Yoer

    # Populate useful items
    if 'id' in session:
        g.dog.me = g.dog.zdb.getUser(session['id'])

        if g.dog.me is None:
            abort(500, "Integrity error - user object lookup failed for user id " + str(session['id']))

    if 'householdId' in session:
        g.dog.hh = g.dog.zdb.getHousehold(session['householdId'])

        if g.dog.hh is None:
            abort(500, "Integrity error - household object lookup failed for household id " + str(session['householdId']))


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# #
# Flask Application Routes
# #

@app.route('/')
def splash():
    return render_template('splash.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if session.get('logged_in'):
            # Attempting to POST to the login screen twice is different than visiting it. Here, we error out because a
            # normal use case of hitting the screen and being redirected to the dashboard is a GET.
            abort(409)  # You can't log in twice...

        if (not request.form.get('inputPassword')) or (not request.form.get('inputUsername')):
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')

        hash = hashlib.pbkdf2_hmac('sha512',
                                   bytearray(request.form['inputPassword'], 'utf-8'),
                                   bytearray(SALT, 'utf-8'),
                                   100000)

        res = db.query_db(queries.CHECK_LOGIN, [request.form['inputUsername'], hash], True)

        if res['COUNT(*)'] > 0:
            # User is now logged in - set session variables and direct to dashboard.
            session['logged_in'] = True

            session['username'] = request.form['inputUsername']
            session['id'] = res['id']

            session['email'] = res['email']

            session['admin'] = shared.isCuteCasaAdmin(session['id'])
            logger.logAdmin("User logged in.", session['id'])

            # Instead of setting household session items here, direct to household selection in order to set them.
            # Household selection menu will check if the person only has one household and will set that as the default.
            return redirect(url_for('household_select'))
        else:
            flash('Invalid username or password.', 'danger')

        return render_template('login.html')
    else:
        if session.get('logged_in'):
            # Navigating to the login view after being logged in - redirect to the dashboard.
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if session.get('logged_in'):
            abort(409)  # You can't register while logged in...

        if not g.dog.zdb.root.globalSettings.registrationEnabled:
            abort(400, 'registration is currently disabled')

        if (
                (not request.form.get('inputPassword')) or
                (not request.form.get('inputUsername')) or
                (not request.form.get('registerEmail'))
        ):
            flash('Please fill in all fields.', 'danger')
            return render_template('register.html')

        if (
                (len(request.form['inputPassword']) <= 3) or
                (len(request.form['inputUsername']) <= 3) or
                (len(request.form['registerEmail']) <= 3)
        ):
            flash("Each item must each be at least 3 characters long.", 'danger')
            return render_template('register.html')

        pwHash = hashlib.pbkdf2_hmac('sha512',
                                   bytearray(request.form['inputPassword'], 'utf-8'),
                                   bytearray(SALT, 'utf-8'),
                                   100000)

        res = db.query_db(queries.CHECK_USERNAME, [request.form['inputUsername'], ], True)

        if res['COUNT(*)'] > 0:
            flash("That username is already in use.", 'danger')
            return render_template('register.html')

        # Unique email is not a requirement.

        # Registration checks out, create ZDB object and DB entry.
        db.post_db(queries.REGISTER, [request.form['inputUsername'],
                                      pwHash,
                                      request.form['registerEmail']])

        g.dog.zdb.createUser(str(db.getLastRowId()), str(request.form['inputUsername']))

        flash("Successfully registered!", 'info')

        return redirect(url_for('login'), code=307) # Redirect while preserving POST
    else:
        return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():  # TODO: Session tokens
    if session.get('logged_in'):
        session.clear()
        return redirect(url_for('splash'))
    abort(401)


@app.route('/floorplan', methods=['GET', 'POST'])
def floorplan():
    """
    The floorplanning view.
    :return: The floorplan template.
    """
    if not session.get('logged_in'):
        abort(401)
    return render_template('floorplan/floorplan.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """
    Render the dashboard view. This will be the home screen that everyone sees upon logging in.
    :return: The render template.
    """
    shared.checkLogin()
    if not session.get('householdId'):
        return redirect(url_for('household_select'))
    return render_template('dashboard.html', members=shared.getUsersForHousehold(session['householdId']))


# ######################################################################################################################
# Routes defined in modules.
# ######################################################################################################################


# ######################################################################################################################
#   User profile and actions.
# ######################################################################################################################


@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    shared.checkLogin()
    return user.profile()

# ######################################################################################################################
#   Household profile and actions.
# ######################################################################################################################


@app.route('/household/select/', methods=['GET'])
@app.route('/household/select/<householdId>', methods=['GET'])
def household_select(householdId=None):
    shared.checkLogin()
    return household.select(householdId)


@app.route('/household/profile', methods=['GET', 'POST'])
def household_profile():
    shared.checkLogin()
    return household.profile()


@app.route('/household/search/<partial>', methods=['GET'])
def household_search(partial):
    shared.checkLogin()
    return household.search(partial)


@app.route('/household/request/<id>')
def household_request(id):
    shared.checkLogin()
    return household.household_request(id)


@app.route('/household/approve/<householdId>/<id>')
def household_approve(householdId, id):
    shared.checkLogin()
    return household.household_approve(householdId, id)


@app.route('/household/deny/<householdId>/<id>')
def household_deny(householdId, id):
    shared.checkLogin()
    return household.household_deny(householdId, id)

# ######################################################################################################################
#   Billing actions.
# ######################################################################################################################

@app.route('/billing/dashboard', methods=['GET'])
def billing_dashboard():
    shared.checkLogin()
    return billing.dashboard()


@app.route('/billing/admin', methods=['GET'])
def billing_admin():
    shared.checkLogin()
    return billing.admin()

@app.route('/billing/billsplit', methods=['GET', 'POST'])
def billing_billsplit():
    shared.checkLogin()
    return billing.billsplit()

@app.route('/billing/billsplit/create', methods=['POST'])
def billing_billsplit_create():
    shared.checkLogin()
    return billing.billsplit_create();

@app.route('/billing/utilities', methods=['GET'])
def billing_utilities():
    shared.checkLogin()
    return billing.utilities()

# ######################################################################################################################
# Admin actions.
# ######################################################################################################################


@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    shared.checkAdmin()
    return admin.dashboard()

@app.route('/admin/logviewer/<logname>/<after>', methods=['GET'])
def admin_logviewer(logname, after):
    shared.checkAdmin()
    return admin.logviewer(logname, after)


@app.route('/admin/nodeviewer/<node>', methods=['GET'], defaults={'index': None})
@app.route('/admin/nodeviewer/<node>/<index>', methods=['GET'])
def admin_nodeviewer(node, index):
    shared.checkAdmin()
    return admin.nodeviewer(node, index)

@app.route('/admin/styletest', methods=['GET'])
def admin_styletest():
    shared.checkAdmin()
    return admin.styletest()

@app.route('/admin/globalSettings', methods=['GET', 'POST'])
def admin_globalSettings():
    shared.checkAdmin()
    return admin.globalSettings()

# ######################################################################################################################
# Final setup and initiation
# ######################################################################################################################

@app.before_first_request
def before_first_request():
    """
    When using the werkzeug reloader, main will run twice because we're being spawned in a subprocess. This causes
    locking issues with zodb, so only initialize it when we're actually ready to process the first request.
    """
    global S_Zdb, S_Yoer

    g.db = connect_db() # Connect to the SQL database to provide logging functionality.
    logger.logSystem("First request received, initializing.")

    # Set up dog object's singletons.
    S_Zdb = zdb.Zdb('secret/cute.zdb')

    if (S_Zdb.root.globalSettings.yoApiKey is not None and S_Zdb.root.globalSettings.yoApiKey != ""):
        S_Yoer = Yoer(S_Zdb.root.globalSettings.yoApiKey)

    db = getattr(g, 'db', None)
    if db is not None:
       db.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)


# #
# Utility methods
# #

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()