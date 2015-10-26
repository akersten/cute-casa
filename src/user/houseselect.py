# ######################################################################################################################
# A user can manage/belong to multiple houses - this is a context screen to prompt the user to select a house, which is
# then populated in the session.
# ######################################################################################################################

from flask import flash, render_template


def houseselect():
    """
    Render the house select view.
    :return: The render template.
    """
    return render_template('user/houseselect.html')
