from flask import flash, render_template, request, session, g, redirect, url_for
import queries


def profile():
    """
    Every household has a profile which can be used to configure global settings for that household.
    Render the household profile view.
    :return: The render template.
    """
    if request.method == 'POST':
        # Check for changes in any of the fields and update them if necessary. If there are errors, keep us on the
        # profile page and show the error. Otherwise, direct us back to the dashboard.

        # Household name.
        if request.form['householdNameInput'] is not None:
            if request.form['householdNameInput'] != session['h_householdName']:
                if len(request.form['householdNameInput']) == 0:
                    flash("Household name must not be blank.")
                    return render_template('household/profile.html')

                # TODO: Sanity check on length

                g.db.execute(queries.HOUSEHOLD_UPDATE_HOUSEHOLDNAME, [request.form['householdNameInput'], session['h_']])
                g.db.commit()
                session['h_householdName'] = request.form['householdNameInput']
                flash("Household name updated.")

        # Household type.
        if request.form['householdTypeInput'] is not None:
            if request.form['householdTypeInput'] != session['h_householdType']:
                if len(request.form['householdTypeInput']) == 0:
                    flash("Household type must not be blank.")
                    return render_template('household/profile.html')

                # TODO: Sanity checks that this is one of the two allowed values.

                g.db.execute(queries.HOUSEHOLD_UPDATE_HOUSEHOLDTYPE, [request.form['householdTypeInput'], session['h_']])
                g.db.commit()
                session['h_householdType'] = request.form['householdTypeInput']
                flash("Household type updated.")

        return redirect(url_for('dashboard'))
    else:
        return render_template('household/profile.html')


def select():
    """
    A user can manage/belong to multiple households - this is a context screen to prompt the user to select a house,
    which is then populated in the session.

    Render the household select view.
    :return: The render template.
    """
    # TODO: CHeck if the user is a member of multiple households.
    # If so, show a menu
    # if not, select just the one and send them to the dashboard. Populate the session variables here.
    return render_template('household/select.html')