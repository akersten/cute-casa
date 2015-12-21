from flask import flash, render_template, request, session, abort, redirect, url_for, jsonify

from src import db
from src import enums
from src import logger
from src import shared
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
            flash('You need a name for your household!', 'danger')
            dead = True

        if not request.form.get('householdTypeInput'):
            flash('You need to select a type for your household!', 'danger')
            dead = True

        if dead:
            # Early exit to avoid trying to use these None variables.
            return render_template('household/profile.html')

        houseName = request.form['householdNameInput']
        houseType = request.form['householdTypeInput']

        if not session.get('householdId'):
            # Creating a new household!
            if len(houseName) < 3:
                flash('The household name is too short.', 'danger')
                dead = True
            elif len(houseName) > 50:
                flash('The household name is too long.', 'danger')
                dead = True

            if not enums.contains(enums.e_household_type, houseType):
                flash(str(houseType) + ' is not a valid house type.', 'danger')
                dead = True

            if dead:
                return render_template('household/profile.html')

            # Create the household!
            db.post_db(queries.HOUSEHOLD_CREATE, [houseName, houseType])
            houseId = db.getLastRowId()

            # Associate this user with the household, as an admin.
            db.post_db(queries.HOUSEHOLD_MEMBERSHIP_ADD, [session['id'], houseId, enums.e_household_relation.admin])


            logger.logAdmin('Created household. Id: ' + str(houseId) + ' Name: ' + houseName, session['id'])
            flash('Household created successfully!', 'info')
            return redirect(url_for('household_select'))

        # TODO: Check if we are an admin of this household and are allowed to make changes to it.

        # Updating an existing household - household name.
        if houseName != session['householdName']:
            if len(houseName) == 0:
                flash("Household name must not be blank.", 'danger')
                return render_template('household/profile.html')
            if len(houseName) > 50:
                flash("Household name is too long.", 'danger')
                return render_template('household/profile.html')

            db.post_db(queries.HOUSEHOLD_UPDATE_HOUSEHOLDNAME, [houseName, session['householdId']])

            session['householdName'] = houseName
            flash("Household name updated.", 'info')

        # Household type.
        if int(houseType) != session['householdType']:
            if not enums.contains(enums.e_household_type, houseType):
                flash(str(houseType) + ' is not a valid house type.', 'danger')
                return render_template('household/profile.html')

            db.post_db(queries.HOUSEHOLD_UPDATE_HOUSEHOLDTYPE, [houseType, session['householdId']])

            session['householdType'] = int(houseType)
            flash("Household type updated.", 'info')

        return redirect(url_for('dashboard'))
    else:
        # The template logic should handle checking if we have selected a household or not.
        users = None
        if session.get('householdId'):
            users = shared.getUsersForHousehold(session['householdId'])

        return render_template('household/profile.html', users=users)


def select(householdId):
    """
    A user can manage/belong to multiple households - this is a context screen to prompt the user to select a house,
    which is then populated in the session.

    Render the household select view.
    :return: The render template.
    """
    if householdId:
        # The user has chosen a house. Make sure they can select this house, set it in the session and redirect to the
        # dashboard.
        if not shared.setHousehold(householdId):
            abort(500)

        return redirect(url_for('dashboard'))
    else:
        households=shared.getHouseholdsForUser(session['id'])

        # TODO: If the person is only a member of one household, just set that household and redirect to the dashboard.
        # TODO: Be careful though - if we came here from the dashboard, we want to not redirect so that the user has
        # the chance to maybe create another household. We can do that when we check the incoming householdId - if it's
        # set, we don't want to auto-redirect because we were already on the dashboard. Set it to None now, because
        # clicking the create new house should go into the profile view with it set to None (otherwise it will edit the
        # "current" (last selected) house).

        if (session.get('householdId')):
            shared.unsetHousehold()

        return render_template('household/select.html', households=households)


def search(partial):
    """
    Search for households containing the partial search.
    :param partial:  The string to search for.
    :return: The households JSON.
    """
    return jsonify(result=db.query_db(queries.HOUSEHOLD_SEARCH, ['%' + partial + '%', ]))

def request(id):
    """
    Request to join this household.
    :param id: The household to join.
    :return: The parameter UR
    """
    # TODO: Validate id and check if we haven't already requested this house, or belong to it, etc.

    flash('Requested to join household!', 'info')
    return redirect(url_for('household_select'))

# ######################################################################################################################
# Household object representation
# ######################################################################################################################

import persistent

class Household(persistent.Persistent):

    def __init__(self, householdId, householdName, householdType):
        # SQL properties
        self.householdId = householdId
        self.householdName = householdName
        self.householdType = householdType

        # Object properties
        self.members = []

    def addMember(self, member):
        self.members

