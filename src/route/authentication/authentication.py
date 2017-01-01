# ######################################################################################################################
# Authentication routes handle login, logout, registration, password recovery, etc. Typically we don't have an existing
# user session here.
# ######################################################################################################################


# noinspection PyUnresolvedReferences
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
#@app.route('/logout', methods=['GET', 'POST'])
def logout():  # TODO: Session tokens
    if session.get('logged_in'):
        session.clear()
        return redirect(url_for('splash'))
    abort(401)
