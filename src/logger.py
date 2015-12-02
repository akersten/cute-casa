# ######################################################################################################################
# Logger
#
# Items can be written to different logs here.
# ######################################################################################################################

from flask import abort

import queries
from src import enums
from src import db

def logAdmin(message, user, level=enums.e_admin_log_event_level.info):
    if not enums.contains(enums.e_admin_log_event_level, level):
        abort(500, "error level not allowed: " + str(level))

    db.post_db(queries.ADMIN_LOG_INSERT, [user, message, level])