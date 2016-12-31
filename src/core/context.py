# ######################################################################################################################
# The global context for the CuteCasa application. This object tracks the global state and singletons for an instance.
# ######################################################################################################################

from core.notification.yo.yoer import Yoer
from shell.shell import ShellContext
from route import routes

from flask import g, Flask


class Context(ShellContext):
    """
    The CuteCasa global context for this instance, to track state and singletons.
    """

    def __init__(self, shell, port=None, dir_static=None, dir_templates=None, db_sql=None, db_object=None):
        """
        Construct a context for this application and initialize the application.
        :param shell: The CuteWorks shell hosting this application.
        :param port: The port to listen on. Looks to environment variables if not defined.
        :param dir_static: The static files directory. Defaults to the project root's /static directory.
        :param dir_templates: The template files directory. Defaults to the project root's /templates directory.
        :param db_sql: The name of the SQL database. Defaults from environment.
        :param db_object: The name of the object database. Defaults from environment.
        """
        super().__init__(shell, port, dir_static, dir_templates, db_sql, db_object)

        # Set up singleton fields specific to the CuteCasa application.
        self._yoer = None

    # region Initialization

    def init_routes(self, flask_app: Flask) -> None:
        """
        Initializes the default routes for the application with the specified Flask application object. We farm this out
        to the __init__.py's of each area's packages (Admin, Billing, etc.).
        :param flask_app: The Flask instance in which to set routes.
        """
        routes.init_routes(flask_app)

    # endregion

    # region Application control

    def _start_impl(self) -> None:
        """
        The target for the context's start method. Starts the Flask application.
        """
        self._flask_app.run(host='0.0.0.0', port=self._port)

    # endregion

    # region Singletons

    def singleton_request_init(self) -> None:
        """
        Set up the singletons on the request object so they accessible in the Flask context.
        :return:
        """
        super().singleton_request_init()

        # The context object (this one) should have methods to get the following singletons. We'll expose them on g.s
        # for ease of access.
        g.s.Yoer = self.singleton_get_yoer()

    def singleton_get_yoer(self) -> Yoer:
        """
        Gets the Yoer object associated with notifications for this application.
        :return: The Yoer object for notifications.
        """
        return self._yoer

    def singleton_set_yoer(self, yoer: Yoer) -> None:
        """
        Sets the yoer notification object associated with the context.
        :param yoer: The yoer notification object to use as the singleton.
        """
        self._yoer = yoer

    # endregion

    # region Global Flask handlers

    def request_before_first(self) -> None:
        """
        Any one-time initialization that we want to run only once when the application context starts. When using the
        werkzeug reloader, main will run twice because we're being spawned in a subprocess. This causes locking issues
        with zodb, so only initialize it when we're actually ready to process the first request. Here, we set up the
        singletons that are more specific to the application context as well. At this point, the database connection is
        not yet open, so we don't want to attempt any accesses to the DB.
        """
        super().request_before_first()

        if not self.singleton_get_zdb().root.globalSettings.yoApiKey:
            self.singleton_set_yoer(Yoer(self.singleton_get_zdb().root.globalSettings.yoApiKey))

    def request_before(self) -> None:
        """
        Do any bringup for things that we need during a request.
        """
        super().request_before()
        # TODO: Run before-request integrity checks.

    # endregion
