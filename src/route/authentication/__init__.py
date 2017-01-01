from flask import Flask

from . import authentication


def init_routes(flask_app: Flask):
    flask_app.add_url_rule("/login", "login", methods=["GET", "POST"], view_func=authentication.login)
    flask_app.add_url_rule("/register", "register", methods=["GET", "POST"], view_func=authentication.register)
    flask_app.add_url_rule("/logout", "logout", methods=["GET"], view_func=authentication.logout)
