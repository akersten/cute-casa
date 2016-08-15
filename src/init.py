import os, hashlib

from cute import init_db,connect_db
from core.database import queries,zdb


# region Initialize SQL database
print('Regenerating CuteCasa DB...')
init_db()
print('Done.')
# endregion

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
