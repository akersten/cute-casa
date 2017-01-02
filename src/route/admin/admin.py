from flask import flash, render_template, request, session, g, redirect, url_for

from core import enums, logger
from core.user import user
from core.database import db, queries


def dashboard():
    """
    The admin dashboard has links to other admin pages. Render the dashboard view.
    :return: The render template.
    """
    logger.logAdmin("Admin dashboard accessed.", session['id'], enums.e_log_event_level.warning)
    return render_template('admin/dashboard.html')


def view_log(logname, after):
    """
    The admin log viewer shows administrative events. Render the logviewer.
    :return: The render template.
    """
    logger.logAdmin('Logviewer (' + logname + ') accessed.', session['id'], enums.e_log_event_level.warning)

    def nameToLog(name):
        return {
            'system': enums.e_log_event_type.system,
            'user': enums.e_log_event_type.user,
            'admin': enums.e_log_event_type.admin,
        }.get(name, '')

    log = nameToLog(logname)

    return render_template('admin/logviewer.html', events=getEvents(log, after, 50),
                           getUserDisplayname=lambda n: user.getUserDisplayname(n),
                           logname=logname,
                           after=int(after),
                           next=int(after)+50,
                           prev=max(int(after)-50, 0))

def view_node(node, index):
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

def settings():
    """
    The page for global settings.
    :return: The render template.
    """

    if request.method == 'POST':
        # Check for updates to the global settings.

        # Display name.
        if request.form['yoApiKeyInput'] is not None:
            if request.form['yoApiKeyInput'] != g.dog.zdb.root.globalSettings.yoApiKey:


                # TODO: Sanity check on length

                g.dog.zdb.root.globalSettings.yoApiKey = request.form['yoApiKeyInput']

                flash("Yo API key updated.", 'info')

        # Registration enabled - checkboxes come in as either 'on' or None >.>
        regEnabled = True if request.form.get('registrationEnabledInput') else False

        if regEnabled != g.dog.zdb.root.globalSettings.registrationEnabled:
            g.dog.zdb.root.globalSettings.registrationEnabled = regEnabled
            flash('Registration ' + ('enabled' if regEnabled else 'disabled') + '.', 'info')

        return redirect(url_for('admin_dashboard'))

    return render_template('admin/globalSettings.html')



def getEvents(log, after, count):
    """
    Return the events after a certain index.
    :param log: The log type to get events for.
    :param after: Index to start events (descending)
    :param count: How many events to pull.
    :return: An array of events.
    """
    if not enums.contains(enums.e_log_event_type, log):
        return None

    return db.query_db(queries.LOG_GET, [log, after, count])



