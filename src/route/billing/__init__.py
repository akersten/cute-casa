from flask import Flask

from . import billing

def init_routes(flask_app: Flask):
    flask_app.add_url_rule("/billing/dashboard", "billing_dashboard", methods=["GET"], view_func=billing.dashboard)
    flask_app.add_url_rule("/billing/admin", "billing_admin", methods=["GET"], view_func=billing.admin)
    flask_app.add_url_rule("/billing/billsplit", "billing_billsplit", methods=["GET", "POST"], view_func=billing.billsplit)
    flask_app.add_url_rule("/billing/billsplit_create", "billing_billsplit_create", methods=["POST"], view_func=billing.billsplit_create)
    flask_app.add_url_rule("/billing/utilities", "billing_utilities", methods=["GET"], view_func=billing.utilities)
