from flask import Flask

from . import user

def init_routes(flask_app: Flask):
    flask_app.add_url_rule("/user/profile", "user_profile", methods=["GET", "POST"], view_func=user.profile)
