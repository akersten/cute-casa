# ######################################################################################################################
# A user manages profile details here, like name, email, alert settings, active houses, and subscription information.
# ######################################################################################################################

from flask import flash, render_template


def profile():
    """
    Render the profile view.
    :return: The render template.
    """
    return render_template('user/profile.html')
