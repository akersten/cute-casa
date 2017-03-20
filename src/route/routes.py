from flask import session, redirect, url_for, render_template, Flask

import route
import route.admin
import route.authentication
import route.billing
import route.household
import route.user

import route.experimental

from route.household import household


def init_routes(flask_app: Flask) -> None:
    """
    Sets up the application routes on the Flask object by looking into each area's package __init__.py and running its
    route initialization.
    :param flask_app: The Flask application.
    """
    route.init_routes(flask_app)
    route.admin.init_routes(flask_app)
    route.authentication.init_routes(flask_app)
    route.billing.init_routes(flask_app)
    route.household.init_routes(flask_app)
    route.user.init_routes(flask_app)

    route.experimental.init_routes(flask_app)
