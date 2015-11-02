from flask import flash, render_template, request, session, g, redirect, url_for
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
                    flash("Display name must not be blank.")
                    return render_template('user/profile.html')

                g.db.execute(queries.USER_UPDATE_DISPLAYNAME, [request.form['displaynameInput'], session['id']])
                g.db.commit()
                session['displayname'] = request.form['displaynameInput']
                flash("Display name updated.")

        # Email.
        if request.form['emailInput'] is not None:
            if request.form['emailInput'] != session['email']:
                g.db.execute(queries.USER_UPDATE_EMAIL, [request.form['emailInput'], session['id']])
                g.db.commit()
                session['email'] = request.form['emailInput']
                flash("Email updated.")

        # Cellphone
        if request.form['cellInput'] is not None:
            if request.form['cellInput'] != session['cellphone']:
                g.db.execute(queries.USER_UPDATE_CELLPHONE, [request.form['cellInput'], session['id']])
                g.db.commit()
                session['cellphone'] = request.form['cellInput']
                flash("Cellphone updated.")

        return redirect(url_for('dashboard'))
    else:
        return render_template('user/profile.html')
