from flask import Flask

from . import household


def init_routes(flask_app: Flask):
    flask_app.add_url_rule("/household/select/<householdId>",
                           "household_select",
                           methods=["GET"],
                           view_func=household.select)

    flask_app.add_url_rule("/household/profile",
                           "household_profile",
                           methods=["GET", "POST"],
                           view_func=household.profile)

    flask_app.add_url_rule("/household/search/<partial>",
                           "household_search",
                           methods=["GET"],
                           view_func=household.search)

    flask_app.add_url_rule("/household/request/join/<householdId>",
                           "household_join",
                           methods=["GET"],
                           view_func=household.request_join)

    flask_app.add_url_rule("/household/request/approve/<householdId>/<userId>",
                           "household_approve",
                           methods=["GET"],
                           view_func=household.request_approve)

    flask_app.add_url_rule("/household/request/deny/<householdId>/<userId>",
                           "household_request_deny",
                           methods=["GET"],
                           view_func=household.request_deny)
