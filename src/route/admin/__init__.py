from flask import Flask

from . import admin


def init_routes(flask_app: Flask):
    flask_app.add_url_rule("/admin/dashboard", "admin_dashboard", methods=["GET"], view_func=admin.dashboard)
    flask_app.add_url_rule("/admin/view/log/<logname>/<after>", "admin_logviewer", methods=["GET"], view_func=admin.view_log)
    flask_app.add_url_rule("/admin/view/node/<node>/<index>", "admin_nodeviewer", methods=["GET"], view_func=admin.view_node)
    flask_app.add_url_rule("/admin/settings", "admin_settings", methods=["GET", "POST"], view_func=admin.settings)
