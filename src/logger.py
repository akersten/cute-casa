# ######################################################################################################################
# Logger
#
# Items can be written to different logs here.
# ######################################################################################################################

from flask import g, abort

import queries
from src import enums

def logAdmin(user, level, message):
    if not enums.contains(enums.e_admin_log_event_level, level):
        abort(500, "error level not allowed: " + str(level))

    g.db.execute(queries.ADMIN_LOG_INSERT, [user, message, level])
    g.db.commit()