# ######################################################################################################################
# Database functionality
#
# Interacting with the database by manually creating queries is overkill for a lot of common operations (like getting
# the value of a single column for a single id), so this file contains implementations of some common access patterns.
#
# These functions rely on consistent naming in the database (e.g. having an id column).
# ######################################################################################################################


def getSingleValue(table, column, id):
    """
    Get a single value out of the database.
    :param table: The table from which to select.
    :param column: The column to select.
    :param id: The id for which to select.
    :return: The single value represented.
    """
    q = "SELECT ? FROM ? WHERE id=?"
    c = g.db.execute(q, [column, table, id])
    e = [dict(res=row[0]) for row in c.fetchall()]
    return e[0]['res']