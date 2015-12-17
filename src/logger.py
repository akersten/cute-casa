# ######################################################################################################################
# Logger
#
# Items can be written to different logs here.
# ######################################################################################################################

from flask import abort, request

import queries
from src import enums
from src import db
from src import shared

def logAdmin(message, user, level=enums.e_admin_log_event_level.info):
    if not enums.contains(enums.e_admin_log_event_level, level):
        abort(500, "error level not allowed: " + str(level))

    db.post_db(queries.ADMIN_LOG_INSERT, [user, message, level])

def logSystem(message, level=enums.e_system_log_event_level.info):
    """
    Logs an event to the system log, and prints it to the screen. If the event level is e_system_log_event_level.crash,
    the server will terminate.
    :param message:
    :param level:
    :return:
    """
    if not enums.contains(enums.e_system_log_event_level, level):
        abort(500, "event level not allowed: " + str(level))

    def levelTag(lev):
        return {
            enums.e_system_log_event_level.warning: 'warning',
            enums.e_system_log_event_level.critical: 'critical',
            enums.e_system_log_event_level.crash: 'CRASH'
        }.get(lev, '')

    print('[' + levelTag(level) + ']: ' + message)
    db.post_db(queries.SYSTEM_LOG_INSERT, [message, level])

    if level is enums.e_system_log_event_level.crash:
        shared.hardstop()

