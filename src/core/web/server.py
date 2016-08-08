from flask import abort, request, g

from core import enums, logger

def softstop():
    """
    Initiate a regular shutdown through the Werkzeug shutdown hook. Existing requests will continue to completion.
    Locks and database will shut down gracefully according to the after_request handler.
    """
    logger.logSystem('--- Soft Stop Initiated ---', enums.e_log_event_level.warning)

    if request is None:
        logger.logSystem('No request present, cannot soft stop.', enums.e_log_event_level.crash)
        hardstop()

    k = request.environ.get('werkzeug.server.shutdown')
    if k is None:
        logger.logSystem('Not running within the Werkzeug server, cannot soft stop.', enums.e_log_event_level.crash)
        hardstop()

    print('- Soft Stop -')
    k()

    abort(500, "CuteCasa - Critical Error, Soft Stop")


def hardstop():
    """
    Try to shut down as fast and minimally as possible,
    :return:
    """

    logger.logSystem('--- Hard Stop Initiated ---', enums.e_log_event_level.critical)

    if g is not None:
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()

    if request is not None:
        k = request.environ.get('werkzeug.server.shutdown')
        k()

    print('--- Hard Stop ---')
    raise SystemExit(0)
