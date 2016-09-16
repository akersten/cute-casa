# ######################################################################################################################
# Initialize the databases and create basic structure for first-time startup. Usually invoked from the command line in
# init.sh.
# ######################################################################################################################

import os
import hashlib
import sqlite3

from contextlib import closing

from core.database import queries, zdb

from shell.shell import Shell
from shell.manifest import Manifest


APP_TITLE = "CuteCasa initialization"
APP_VERSION = "0.0.0"
APP_PREFIX = "CUTECASA"

shell = Shell(Manifest(APP_TITLE, APP_VERSION, APP_PREFIX))

if not shell.env_expect([
    "SQL_DATABASE",
    "SQL_SCHEMA"
]):
    print("Missing required environment variable.")
    quit(1)


def connect_db():
    """
    Connect to the SQL database in order to insert the schema.
    """
    return sqlite3.connect(shell.env_get("SQL_DATABASE"))


def init_db():
    """
    Initialize the SQL database with the CuteCasa schema.
    """
    with closing(connect_db()) as db:
        with open(shell.env_get('SQL_SCHEMA'), mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# region Initialize SQL database

print('Regenerating CuteCasa DB...')
init_db()
print('Done.')

# endregion

















quit(0)

# region Create admin user
# Shouldn't have to worry about duplicate users here, this should be the first user in the database.

yn = input('Create admin user? [y/N] ')
if yn not in ['Y', 'y', 'yes', 'Yes']:
    exit(0)

adminName = input('Admin user name: ')
adminPass = input('Admin user password: ')
adminEmail = input('Admin user email: ')

if adminName is not None and adminPass is not None and adminEmail is not None:


    # TODO: REFACTOR THIS - it should really be part of a CuteContext from where we can access both databases seamlessly
    # without having to bring connections up and down manually. also the creation of objects should be abstracted and
    # just passed a shell, the Context has the handles to the databases that it will maintain.... Static methods will
    # just look at that for whatever their database needs are.

    pwHash = hashlib.pbkdf2_hmac('sha512',
                           bytearray(adminPass, 'utf-8'),
                           bytearray(os.environ.get('CUTE_SALT'), 'utf-8'),
                           100000)

    db = connect_db()
    db.post_db(queries.REGISTER, [adminName, pwHash, adminEmail])

    z = zdb.Zdb(os.environ.get('CUTE_ZDB'))
    z.createUser(str(db.getLastRowId()), adminName)

    db.close()
    print('Admin user created.')
# endregion
