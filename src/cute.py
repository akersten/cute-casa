# ######################################################################################################################
# The application entry point. Run this via cute.sh so that environment variables are set.
# ######################################################################################################################

import os
import sqlite3

from contextlib import closing

from core import enums, logger
from core.database import zdb
from core.notification.yo.yoer import Yoer
from flask import Flask, session, g, redirect, url_for, flash

VERSION = "0.0.0"

# Create the cute context


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

# ######################################################################################################################
# Initialize the Flask application routes as defined in the routes file.
# ######################################################################################################################

with open(os.path.dirname(os.path.realpath(__file__)) + '/route.py') as f:
    code = compile(f.read(), 'route.py', 'exec')
    exec(code)

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