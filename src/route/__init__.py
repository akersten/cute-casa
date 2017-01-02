from flask import Flask

from . import generic


def init_routes(flask_app: Flask):
    flask_app.add_url_rule("/", "splash", methods=["GET"], view_func=generic.splash)
    flask_app.add_url_rule("/dashboard", "dashboard", methods=["GET", "POST"], view_func=generic.dashboard)
