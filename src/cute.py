# ######################################################################################################################
# The CuteCasa application bootstrapper & entry point. Sets up the application context and starts the Flask engine. Run
# this via cute.sh so that environment variables are set for the context.
# ######################################################################################################################

import os
import sqlite3

from contextlib import closing

from core import logger
from core.context import Context
from core.database import zdb
from core.notification.yo.yoer import Yoer

from shell.shell import Shell
from shell.manifest import Manifest

from flask import Flask, g


# ######################################################################################################################
# First, set up the application shell and read configuration from environment variables set in the secret shell script
# that we don't commit. Then, set some Flask configuration variables that get read from this namespace, and create the
# Flask application with the appropriate request handlers and hooks.
# ######################################################################################################################

APP_TITLE = "CuteCasa"
APP_VERSION = "0.0.0"
APP_PREFIX = "CUTECASA_"

DIR_TEMPLATES = "../templates"
DIR_STATIC = "../static"

shell = Shell(Manifest(APP_TITLE, APP_VERSION, APP_PREFIX))
context = Context()
shell.set_context(context)

DEBUG = shell.get_env('DEBUG')
SECRET_KEY = shell.get_env('SECRET_KEY')

app = Flask(__name__, template_folder=DIR_TEMPLATES, static_folder=DIR_STATIC)
app.config.from_object(__name__)


@app.before_request
def before_request():
    """
    Make the shell & context available on each request, and also bringup/teardown any non-singleton db connections.
    :return:
    """
    g.shell = shell
    g.context = context

    context.begin_request()


@app.teardown_request
def teardown_request(exception):
    """
    Tell the context that this request is ending so it can do any cleanup it needs to.
    """
    context.after_request(exception)

# ######################################################################################################################
# Initialize the Flask application routes as defined in the routes file.
# ######################################################################################################################

with open(os.path.dirname(os.path.realpath(__file__)) + '/route.py') as f:
    code = compile(f.read(), 'route.py', 'exec')
    exec(code)


















def connect_db():
    return sqlite3.connect(context.get_env("SQL_DATABASE"))






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
    S_Zdb = zdb.Zdb(context.get_env("OBJECT_DATABASE"))

    if (S_Zdb.root.globalSettings.yoApiKey is not None and S_Zdb.root.globalSettings.yoApiKey != ""):
        S_Yoer = Yoer(S_Zdb.root.globalSettings.yoApiKey)

    db = getattr(g, 'db', None)
    if db is not None:
       db.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(context.get_env('PORT')))


# #
# Utility methods
# #

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('../config/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()