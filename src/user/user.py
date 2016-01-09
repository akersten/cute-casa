from flask import flash, render_template, request, session, g, redirect, url_for

from src import db
import queries


def profile():
    """
    A user manages profile details here, like name, email, alert settings, active houses, and subscription information.
    Render the profile view.
    :return: The render template.
    """
    if request.method == 'POST':
        # Check for changes in any of the fields and update them if necessary. If there are errors, keep us on the
        # profile page and show the error. Otherwise, direct us back to the dashboard.

        # Display name.
        if request.form['displaynameInput'] is not None:
            if request.form['displaynameInput'] != session['displayname']:
                if len(request.form['displaynameInput']) == 0:
                    flash("Display name must not be blank.", 'danger')
                    return render_template('user/profile.html')

                # TODO: Sanity check on length

                db.post_db(queries.USER_UPDATE_DISPLAYNAME, [request.form['displaynameInput'], session['id']])
                session['displayname'] = request.form['displaynameInput']
                flash("Display name updated.", 'info')

        # Email.
        if request.form['emailInput'] is not None:
            if request.form['emailInput'] != session['email']:

                # TODO: Sanity check on length

                db.post_db(queries.USER_UPDATE_EMAIL, [request.form['emailInput'], session['id']])
                session['email'] = request.form['emailInput']
                flash("Email updated.", 'info')

        # Cellphone
        if request.form['cellInput'] is not None:
            if request.form['cellInput'] != session['cellphone']:

                # TODO: Sanity check on length

                db.post_db(queries.USER_UPDATE_CELLPHONE, [request.form['cellInput'], session['id']])

                session['cellphone'] = request.form['cellInput']
                flash("Cellphone updated.", 'info')

        return redirect(url_for('dashboard'))
    else:
        return render_template('user/profile.html')

# ######################################################################################################################
# User object representation
# ######################################################################################################################

import persistent, transaction

class User(persistent.Persistent):

    def __init__(self, id):
        if id is None or id == '':
            raise ValueError('Users must have an id.')

        self.id = id



    @property
    def yoUsername(self):
        return self._yoUsername
    @yoUsername.setter
    def yoUsername(self, yoUsername):
        self._yoUsername = yoUsername
        transaction.commit()

