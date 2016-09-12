import hashlib

from flask import session, redirect, url_for, render_template, abort, request, flash

from core import logger
from core.database import db, queries
from core.user import user

from route.admin import admin
from route.household import household
from route.billing import billing


# noinspection PyUnresolvedReferences
@app.route('/')
def splash():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    print(app.template_folder)
    return render_template('splash.html')


# noinspection PyUnresolvedReferences
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if session.get('logged_in'):
            # Attempting to POST to the login screen twice is different than visiting it. Here, we error out because a
            # normal use case of hitting the screen and being redirected to the dashboard is a GET.
            abort(409)  # You can't log in twice...

        if (not request.form.get('inputPassword')) or (not request.form.get('inputUsername')):
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')

        hash = hashlib.pbkdf2_hmac('sha512',
                                   bytearray(request.form['inputPassword'], 'utf-8'),
                                   bytearray(context.get_env('SALT'), 'utf-8'),
                                   100000)

        res = db.query_db(queries.CHECK_LOGIN, [request.form['inputUsername'], hash], True)

        if res['COUNT(*)'] > 0:
            # User is now logged in - set session variables and direct to dashboard.
            session['logged_in'] = True

            session['username'] = request.form['inputUsername']
            session['id'] = res['id']

            session['email'] = res['email']

            session['admin'] = user.isCuteCasaAdmin(session['id'])
            logger.logAdmin("User logged in.", session['id'])

            # Instead of setting household session items here, direct to household selection in order to set them.
            # Household selection menu will check if the person only has one household and will set that as the default.
            return redirect(url_for('household_select'))
        else:
            flash('Invalid username or password.', 'danger')

        return render_template('login.html')
    else:
        if session.get('logged_in'):
            # Navigating to the login view after being logged in - redirect to the dashboard.
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html')


# noinspection PyUnresolvedReferences
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if session.get('logged_in'):
            abort(409)  # You can't register while logged in...

        if not g.dog.zdb.root.globalSettings.registrationEnabled:
            abort(400, 'registration is currently disabled')

        if (
                (not request.form.get('inputPassword')) or
                (not request.form.get('inputUsername')) or
                (not request.form.get('registerEmail'))
        ):
            flash('Please fill in all fields.', 'danger')
            return render_template('register.html')

        if (
                (len(request.form['inputPassword']) <= 3) or
                (len(request.form['inputUsername']) <= 3) or
                (len(request.form['registerEmail']) <= 3)
        ):
            flash("Each item must each be at least 3 characters long.", 'danger')
            return render_template('register.html')

        pwHash = hashlib.pbkdf2_hmac('sha512',
                                   bytearray(request.form['inputPassword'], 'utf-8'),
                                   bytearray(context.get_env('SALT'), 'utf-8'),
                                   100000)

        res = db.query_db(queries.CHECK_USERNAME, [request.form['inputUsername'], ], True)

        if res['COUNT(*)'] > 0:
            flash("That username is already in use.", 'danger')
            return render_template('register.html')

        # Unique email is not a requirement.

        # Registration checks out, create ZDB object and DB entry.
        db.post_db(queries.REGISTER, [request.form['inputUsername'],
                                      pwHash,
                                      request.form['registerEmail']])

        g.dog.zdb.createUser(str(db.getLastRowId()), str(request.form['inputUsername']))

        flash("Successfully registered!", 'info')

        return redirect(url_for('login'), code=307) # Redirect while preserving POST
    else:
        return render_template('register.html')


# noinspection PyUnresolvedReferences
@app.route('/logout', methods=['GET', 'POST'])
def logout():  # TODO: Session tokens
    if session.get('logged_in'):
        session.clear()
        return redirect(url_for('splash'))
    abort(401)


# noinspection PyUnresolvedReferences
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """
    Render the dashboard view. This will be the home screen that everyone sees upon logging in.
    :return: The render template.
    """
    user.checkLogin()
    if not session.get('householdId'):
        return redirect(url_for('household_select'))
    return render_template('dashboard.html', members=household.getUsersForHousehold(session['householdId']))

# ######################################################################################################################
#   User profile and actions.
# ######################################################################################################################

# noinspection PyUnresolvedReferences
@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    user.checkLogin()
    return user.profile()

# ######################################################################################################################
#   Household profile and actions.
# ######################################################################################################################

# noinspection PyUnresolvedReferences
@app.route('/household/select/', methods=['GET'])
@app.route('/household/select/<householdId>', methods=['GET'])
def household_select(householdId=None):
    user.checkLogin()
    return household.select(householdId)

# noinspection PyUnresolvedReferences
@app.route('/household/profile', methods=['GET', 'POST'])
def household_profile():
    user.checkLogin()
    return household.profile()

# noinspection PyUnresolvedReferences
@app.route('/household/search/<partial>', methods=['GET'])
def household_search(partial):
    user.checkLogin()
    return household.search(partial)

# noinspection PyUnresolvedReferences
@app.route('/household/request/<id>')
def household_request(id):
    user.checkLogin()
    return household.household_request(id)

# noinspection PyUnresolvedReferences
@app.route('/household/approve/<householdId>/<id>')
def household_approve(householdId, id):
    user.checkLogin()
    return household.household_approve(householdId, id)

# noinspection PyUnresolvedReferences
@app.route('/household/deny/<householdId>/<id>')
def household_deny(householdId, id):
    user.checkLogin()
    return household.household_deny(householdId, id)

# ######################################################################################################################
#   Billing actions.
# ######################################################################################################################

# noinspection PyUnresolvedReferences
@app.route('/billing/dashboard', methods=['GET'])
def billing_dashboard():
    user.checkLogin()
    return billing.dashboard()

# noinspection PyUnresolvedReferences
@app.route('/billing/admin', methods=['GET'])
def billing_admin():
    user.checkLogin()
    return billing.admin()

# noinspection PyUnresolvedReferences
@app.route('/billing/billsplit', methods=['GET', 'POST'])
def billing_billsplit():
    user.checkLogin()
    return billing.billsplit()

# noinspection PyUnresolvedReferences
@app.route('/billing/billsplit/create', methods=['POST'])
def billing_billsplit_create():
    user.checkLogin()
    return billing.billsplit_create()

# noinspection PyUnresolvedReferences
@app.route('/billing/utilities', methods=['GET'])
def billing_utilities():
    user.checkLogin()
    return billing.utilities()

# ######################################################################################################################
# Admin actions.
# ######################################################################################################################

# noinspection PyUnresolvedReferences
@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    user.checkAdmin()
    return admin.dashboard()

# noinspection PyUnresolvedReferences
@app.route('/admin/logviewer/<logname>/<after>', methods=['GET'])
def admin_logviewer(logname, after):
    user.checkAdmin()
    return admin.logviewer(logname, after)

# noinspection PyUnresolvedReferences
@app.route('/admin/nodeviewer/<node>', methods=['GET'], defaults={'index': None})
@app.route('/admin/nodeviewer/<node>/<index>', methods=['GET'])
def admin_nodeviewer(node, index):
    user.checkAdmin()
    return admin.nodeviewer(node, index)

# noinspection PyUnresolvedReferences
@app.route('/admin/styletest', methods=['GET'])
def admin_styletest():
    user.checkAdmin()
    return admin.styletest()

# noinspection PyUnresolvedReferences
@app.route('/admin/globalSettings', methods=['GET', 'POST'])
def admin_globalSettings():
    user.checkAdmin()
    return admin.globalSettings()