# ######################################################################################################################
# Database functionality
#
# Interacting with the database by manually creating queries is overkill for a lot of common operations (like getting
# the value of a single column for a single id), so this file contains implementations of some common access patterns.
#
# These functions rely on consistent naming in the database (e.g. having an id column).
# ######################################################################################################################

from flask import g, abort

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    ret = [make_dicts(cur, row) for row in rv]
    cur.close()
    return (ret[0] if ret else None) if one else ret

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def post_db(query, args=()):
    cur = g.db.execute(query, args)
    g.db.commit()
    cur.close()


ALLOWED_DYNAMIC_TABLES = ["users", "households", "household_memberships", "admin_log_events"]

def cleanTable(table):
    """
    It is not possible to parameterize tables in a prepared statement, but we still need to insert them dynamically.
    Validate that the given value is allowed to be in the query.
    :param table: The table name to check.
    :return: The table name, if it is the name of an allowed table. Aborts otherwise.
    """
    if not table in ALLOWED_DYNAMIC_TABLES:
        abort(500, "not an allowed table")
    return table

def getSingleValue(table, column, id):
    """
    Get a single value out of the database.
    :param table: The table from which to select.
    :param column: The column to select.
    :param id: The id for which to select.
    :return: The single value represented.
    """
    q = "SELECT * FROM " + cleanTable(table) + " WHERE id = ?"
    return query_db(q, [id,], True)[column]