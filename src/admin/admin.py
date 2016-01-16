from flask import flash, render_template, request, session, g, redirect, url_for

from src import shared
from src import db
from src import logger
from src import enums
import queries


def dashboard():
    """
    The admin dashboard has links to other admin pages. Render the dashboard view.
    :return: The render template.
    """
    logger.logAdmin("Admin dashboard accessed.", session['id'], enums.e_log_event_level.warning)
    return render_template('admin/dashboard.html')


def logviewer(logname, after):
    """
    The admin log viewer shows administrative events. Render the logviewer.
    :return: The render template.
    """
    logger.logAdmin('Logviewer (' + logname + ') accessed.', session['id'], enums.e_log_event_level.warning)
    return render_template('admin/logviewer.html', events=getEvents(logname, after, 50),
                                                    getUserDisplayname=lambda n: shared.getUserDisplayname(n),
                                                    logname=logname,
                                                    after=int(after),
                                                    next=int(after)+50,
                                                    prev=max(int(after)-50, 0))

def nodeviewer(node, index):
    """
    The node viewer shows a node in z.dog.zdb.root . Right now, only first-level objects, first-level iterables,
    and objects stored in first-level iterables are supported (e.g. a btree inside a btree won't look right when
    viewed with this).
    :param node: The name of the node to display, e.g. 'households', 'globalSettings'.
    :param index: The subscript of the node to display, e.g. '1', '2'
    :return: The render template.
    """
    logger.logAdmin('View ZDB node ' + str(node), session['id'], enums.e_log_event_level.info)

    #children = [c for c in dir(getattr(g.dog.zdb, node)) if not c.startswith('_')]
    if index is None:
        # First level iterable or object.
        try:
            # Iteratable
            children = [(c, None) for c in getattr(g.dog.zdb.root, node)]
        except TypeError:
            # Object
            children = [(c, getattr(getattr(g.dog.zdb.root, node),c) or ' ') for c in dir(getattr(g.dog.zdb.root, node)) if not c.startswith('_')]
    else:
        # Second level object
        children = [(c, getattr(getattr(g.dog.zdb.root, node)[index],c) or ' ') for c in dir(getattr(g.dog.zdb.root, node)[index]) if not c.startswith('_')]

    return render_template('admin/nodeviewer.html', node=node, children=children, index=index)

def styletest():
    """
    A page with all of our styles in one place to test how things look.
    :return: The render template.
    """
    return render_template('admin/styletest.html')

def globalSettings():
    """
    The page for global settings.
    :return: The render template.
    """
    return render_template('admin/globalSettings.html')



def getEvents(logname, after, count):
    """
    Return the events after a certain index.
    :param after: Index to start events (descending)
    :param count: How many events to pull.
    :return: An array of events.
    """
    if logname == "system":
        return db.query_db(queries.SYSTEM_LOG_GET, [after, count])
    elif logname == "admin":
        return db.query_db(queries.ADMIN_LOG_GET, [after, count])
    else:
        return None


