# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from contextlib import closing

import os
import queries
import hashlib
import array

VERSION = "0.0.0"

# Read configuration from environment variables - these are set by the secret script that we don't commit...
DATABASE = os.environ.get('CUTE_DB')
DEBUG = os.environ.get('CUTE_DEBUG') in ['True', 'true', '1', 'yes']
SECRET_KEY = os.environ.get('CUTE_SECRET_KEY')
USERNAME = os.environ.get('CUTE_USERNAME')
PASSWORD = os.environ.get('CUTE_PASSWORD')
PORT = os.environ.get('CUTE_PORT')
SALT = os.environ.get('CUTE_SALT')


def notSet(problem):
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


@app.route('/')
def splash():
    return render_template('splash.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if session.get('logged_in'):
            abort(409)  # You can't log in twice...

        if (request.form['loginPassword'] is None) or (request.form['loginName'] is None):
            abort(400)

        hash = hashlib.pbkdf2_hmac('sha512', \
                                   bytearray(request.form['loginPassword'], 'utf-8'), \
                                   bytearray(SALT, 'utf-8'), \
                                   100000)

        c = g.db.execute(queries.CHECK_LOGIN, [request.form['loginName'], hash])
        e = [dict(count=row[0]) for row in c.fetchall()]

        if e[0]['count'] > 0:
            flash("valid (" + str(e[0]['count']) + ")")

            session['logged_in'] = True
        else:
            flash("invalid (" + str(e[0]['count']) + ")")

        return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():  # TODO: Session tokens
    if session.get('logged_in'):
        session.pop('logged_in')
        return redirect(url_for('splash'))
    abort(401)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
