from flask import flash, render_template


def profile():
    """
    Every household has a profile which can be used to configure global settings for that household.
    Render the household profile view.
    :return: The render template.
    """
    return render_template('household/profile.html')


def select():
    """
    A user can manage/belong to multiple households - this is a context screen to prompt the user to select a house,
    which is then populated in the session.

    Render the household select view.
    :return: The render template.
    """
    return render_template('household/select.html')