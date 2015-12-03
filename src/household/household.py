from flask import flash, render_template, request, session, abort, redirect, url_for

from src import db
from src import enums
from src import logger
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

        # Check that fields have been filled out correctly.

        dead = False

        if not request.form.get('householdNameInput'):
            flash('You need a name for your household!')
            dead = True

        if not request.form.get('householdTypeInput'):
            flash('You need to select a type for your household!')
            dead = True

        if dead:
            # Early exit to avoid trying to use these None variables.
            return render_template('household/profile.html')

        houseName = request.form['householdNameInput']
        houseType = request.form['householdTypeInput']

        if not session.get('householdId'):
            # Creating a new household!
            if len(houseName) < 3:
                flash('The household name is too short.')
                dead = True
            elif len(houseName) > 50:
                flash('The household name is too long.')
                dead = True

            if not enums.contains(enums.e_household_type, houseType):
                flash(str(houseType) + ' is not a valid house type.')
                dead = True

            if dead:
                return render_template('household/profile.html')

            # Create the household!
            db.post_db(queries.HOUSEHOLD_CREATE, [houseName, houseType])
            houseId = db.getLastRowId()

            # Associate this user with the household, as an admin.
            db.post_db(queries.HOUSEHOLD_MEMBERSHIP_ADD, [session['id'], houseId, enums.e_household_relation.admin])


            logger.logAdmin('Created household. Id: ' + str(houseId) + ' Name: ' + houseName, session['id'])
            flash('Household created successfully!')
            return redirect(url_for('household_select'))

        # TODO: Check if we are an admin of this household and are allowed to make changes to it.

        # Updating an existing household - household name.
        if houseName != session['householdName']:
            if len(houseName) == 0:
                flash("Household name must not be blank.")
                return render_template('household/profile.html')
            if len(houseName) > 50:
                flash("Household name is too long.")
                return render_template('household/profile.html')

            db.post_db(queries.HOUSEHOLD_UPDATE_HOUSEHOLDNAME, [houseName, session['householdId']])

            session['householdName'] = houseName
            flash("Household name updated.")

        # Household type.
        if houseType != session['householdType']:
            if not enums.contains(enums.e_household_type, houseType):
                flash(str(houseType) + ' is not a valid house type.')
                return render_template('household/profile.html')

            db.post_db(queries.HOUSEHOLD_UPDATE_HOUSEHOLDTYPE, [houseType, session['householdId']])

            session['householdType'] = houseType
            flash("Household type updated.")

        return redirect(url_for('dashboard'))
    else:
        # Check if we've selected a household or not'
        # The template logic should handle most of what we need to do here.
        #TODO
        return render_template('household/profile.html')


def select():
    """
    A user can manage/belong to multiple households - this is a context screen to prompt the user to select a house,
    which is then populated in the session.

    Render the household select view.
    :return: The render template.
    """
    if request.method == 'POST':
        # The user has chosen a house. Make sure they can select this house, set it in the session and redirect to the
        # dashboard.
        abort(403) #TODO remove this just temporary so it doesn't crash
    else:
        return render_template('household/select.html')
    # TODO: CHeck if the user is a member of multiple households.
    # If so, show a menu
    # if not, select just the one and send them to the dashboard. Populate the session variables here.
