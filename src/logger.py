# ######################################################################################################################
# Logger
#
# Items can be written to different logs here.
# ######################################################################################################################

from flask import abort, request

import queries
from os import environ
from src import enums
from src import db
from src import shared

def _log(message, log, level=enums.e_log_event_level, print=False, user=None):
    """
    Internal helper method that actually does the logging of the event. If the event level is e_log_event_level.crash,
    the server will terminate.
    :param message: The message to log.
    :param log: Which log to log the message to.
    :param level: The event importance.
    :param user: The user ID that caused this event.
    :param print: Whether to print the message to the screen by default.
    """
    if environ.get('CUTECASA_TEST'):
        return

    if not enums.contains(enums.e_log_event_type, log):
        abort(500, 'Log type not allowed: ' + str(log))

    if not enums.contains(enums.e_log_event_level, level):
        abort(500, 'Error level not allowed: ' + str(level))

    def levelTag(lev):
        return {
            enums.e_log_event_level.warning: 'warn',
            enums.e_log_event_level.critical: 'critical',
            enums.e_log_event_level.crash: 'CRASH',
        }.get(lev, '')

    def logTag(l):
        return {
            enums.e_log_event_type.user: 'user',
            enums.e_log_event_type.system: 'sys',
            enums.e_log_event_type.admin: 'ADMIN'
        }.get(log, '')

    if print or level == enums.e_log_event_level.crash:
        print('[' + levelTag(level) + '][' + logTag(log) + ']: ' + message)

    db.post_db(queries.LOG_INSERT, [user, message, level])

    if level == enums.e_log_event_level.crash:
        shared.hardstop()


def logAdmin(message, user, level=enums.e_log_event_level.info):
    """
    Logs an event to the admin log, and prints it to the screen.
    :param message: The message to log.
    :param user: The user ID that caused this event.
    :param level: The event importance.
    """
    _log(message, enums.e_log_event_type.admin, level, True)

def logSystem(message, level=enums.e_log_event_level.info):
    """
    Logs an event to the system log, and prints it to the screen.
    :param message: The message to log.
    :param level: The event importance.
    """
    _log(message, enums.e_log_event_type.system, level, True)

def logUser(message, user, level=enums.e_log_event_level.info):
    """
    Logs an event to the user log.
    :param message: The message to log.
    :param user: The user ID that caused this event.
    :param level: The event importance.
    """
    _log(message, enums.e_log_event_type.user, level)

