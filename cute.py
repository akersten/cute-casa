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
from src import logger
from src import enums
from src.user import user
from src.household import household
from src.billing import billing
from src.admin import admin

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


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()



# #
# Global template functions
# #
flasherstr = """
 {% with messages = get_flashed_messages(with_categories=True) %}
                        {% if messages %}
                            <!-- Realistically, category will never be blank and we'll never default in 'info'
                                 (because the default Flask flash category is 'message'), but it's good style. -->
                            {% for category, message in messages %}

                                <div class="alert alert-{{ category | default('info') }}" style="margin-top: 1em;">
                                    <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
                                <p>{{ message }}</p>
                            </div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
"""
def flasher():
    """
    The flashed messages reader that should go in almost all of the templates somewhere (use {{ flasher() }}
    :return: The Jinja2 flasher template.
    """
    return flasherstr
app.jinja_env.globals.update(flasher=flasher)


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

        if (not request.form.get('loginPassword')) or (not request.form.get('loginUsername')):
            abort(400)

        hash = hashlib.pbkdf2_hmac('sha512',
                                   bytearray(request.form['loginPassword'], 'utf-8'),
                                   bytearray(SALT, 'utf-8'),
                                   100000)

        res = db.query_db(queries.CHECK_LOGIN, [request.form['loginUsername'], hash], True)

        if res['COUNT(*)'] > 0:
            # User is now logged in - set session variables and direct to dashboard.
            session['logged_in'] = True

            session['username'] = request.form['loginUsername']
            session['id'] = res['id']

            session['email'] = res['email']
            session['cellphone'] = res['cellphone']
            session['displayname'] = res['displayname']

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

        if (
                (not request.form.get('registerPassword')) or
                (not request.form.get('registerUsername')) or
                (not request.form.get('registerEmail'))
        ):
            abort(400)

        if (
                (len(request.form['registerPassword']) <= 3) or
                (len(request.form['registerUsername']) <= 3) or
                (len(request.form['registerEmail']) <= 3)
        ):
            flash("Each item must each be at least 3 characters long.", 'danger')
            return render_template('register.html')

        pwHash = hashlib.pbkdf2_hmac('sha512',
                                   bytearray(request.form['registerPassword'], 'utf-8'),
                                   bytearray(SALT, 'utf-8'),
                                   100000)

        res = db.query_db(queries.CHECK_USERNAME, [request.form['registerUsername'], ], True)

        if res['COUNT(*)'] > 0:
            flash("That username is already in use.", 'danger')
            return render_template('register.html')

        db.post_db(queries.REGISTER, [request.form['registerUsername'],
                                      request.form['registerUsername'],
                                      pwHash,
                                      request.form['registerEmail']])

        flash("Successfully registered!", 'info')

        return render_template('register.html')
    else:
        return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():  # TODO: Session tokens
    if session.get('logged_in'):
        session.pop('logged_in')
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
    return render_template('dashboard.html')


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

# ######################################################################################################################
#   Billing actions.
# ######################################################################################################################


@app.route('/billing/billsplit', methods=['GET', 'POST'])
def billing_billsplit():
    shared.checkLogin()
    return billing.billsplit()

# ######################################################################################################################
# Admin actions.
# ######################################################################################################################


@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    shared.checkAdmin()
    return admin.dashboard()

@app.route('/admin/logviewer/<after>', methods=['GET'])
def admin_logviewer(after):
    shared.checkAdmin()
    return admin.logviewer(after)


# ######################################################################################################################
# Final setup and initiation
# ######################################################################################################################

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
