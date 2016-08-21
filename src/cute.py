# ######################################################################################################################
# The application entry point. Run this via cute.sh so that environment variables are set.
# ######################################################################################################################

import hashlib
import os
import sqlite3

from contextlib import closing

from core import enums, logger
from core.database import db, zdb
from core.notification.yo.yoer import Yoer
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

from route.admin import admin
from route.billing import billing
from route.household import household
from core.user import user
from core.database import queries

VERSION = "0.0.0"

# Read configuration from environment variables - these are set by the secret script that we don't commit...
DATABASE = os.environ.get('CUTE_DB')
ZDATABASE = os.environ.get('CUTE_ZDB')
DEBUG = (os.environ.get('CUTE_DEBUG') in ['True', 'true', '1', 'yes'])
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

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


# Bringup and teardown
@app.before_request
def before_request():
    g.db = connect_db()

    # Add singleton references to dog object.
    # TODO: Init this with the static cutectx.
    g.dog = lambda: None
    g.dog.zdb = S_Zdb
    g.dog.yoer = S_Yoer


    # TODO: We need to just force a logout here since the user probably doesn't exit

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
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    print(app.template_folder)
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

            session['admin'] = user.isCuteCasaAdmin(session['id'])
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


@app.route('/dashboard', methods=['GET', 'POST'])
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
# Routes defined in modules.
# ######################################################################################################################


# ######################################################################################################################
#   User profile and actions.
# ######################################################################################################################


@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    user.checkLogin()
    return user.profile()

# ######################################################################################################################
#   Household profile and actions.
# ######################################################################################################################


@app.route('/household/select/', methods=['GET'])
@app.route('/household/select/<householdId>', methods=['GET'])
def household_select(householdId=None):
    user.checkLogin()
    return household.select(householdId)


@app.route('/household/profile', methods=['GET', 'POST'])
def household_profile():
    user.checkLogin()
    return household.profile()


@app.route('/household/search/<partial>', methods=['GET'])
def household_search(partial):
    user.checkLogin()
    return household.search(partial)


@app.route('/household/request/<id>')
def household_request(id):
    user.checkLogin()
    return household.household_request(id)


@app.route('/household/approve/<householdId>/<id>')
def household_approve(householdId, id):
    user.checkLogin()
    return household.household_approve(householdId, id)


@app.route('/household/deny/<householdId>/<id>')
def household_deny(householdId, id):
    user.checkLogin()
    return household.household_deny(householdId, id)

# ######################################################################################################################
#   Billing actions.
# ######################################################################################################################

@app.route('/billing/dashboard', methods=['GET'])
def billing_dashboard():
    user.checkLogin()
    return billing.dashboard()


@app.route('/billing/admin', methods=['GET'])
def billing_admin():
    user.checkLogin()
    return billing.admin()

@app.route('/billing/billsplit', methods=['GET', 'POST'])
def billing_billsplit():
    user.checkLogin()
    return billing.billsplit()

@app.route('/billing/billsplit/create', methods=['POST'])
def billing_billsplit_create():
    user.checkLogin()
    return billing.billsplit_create();

@app.route('/billing/utilities', methods=['GET'])
def billing_utilities():
    user.checkLogin()
    return billing.utilities()

# ######################################################################################################################
# Admin actions.
# ######################################################################################################################


@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    user.checkAdmin()
    return admin.dashboard()

@app.route('/admin/logviewer/<logname>/<after>', methods=['GET'])
def admin_logviewer(logname, after):
    user.checkAdmin()
    return admin.logviewer(logname, after)


@app.route('/admin/nodeviewer/<node>', methods=['GET'], defaults={'index': None})
@app.route('/admin/nodeviewer/<node>/<index>', methods=['GET'])
def admin_nodeviewer(node, index):
    user.checkAdmin()
    return admin.nodeviewer(node, index)

@app.route('/admin/styletest', methods=['GET'])
def admin_styletest():
    user.checkAdmin()
    return admin.styletest()

@app.route('/admin/globalSettings', methods=['GET', 'POST'])
def admin_globalSettings():
    user.checkAdmin()
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
    S_Zdb = zdb.Zdb(app.config['ZDATABASE'])

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
        with app.open_resource('../config/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()