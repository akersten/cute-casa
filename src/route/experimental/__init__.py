from flask import Flask
import route.generic

def init_routes(flask_app: Flask):
    # Experimental routes should only be enabled if we are running in debug mode.
    if not flask_app.config:
        return

    flask_app.add_url_rule("/experimental/sample_components",
                           "experimental_sample_components",
                           methods=["GET"],
                           view_func=lambda: route.generic.generic_path_render("experimental/sample_components.html"))
