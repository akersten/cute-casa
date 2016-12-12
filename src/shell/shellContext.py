# ######################################################################################################################
# The shell launches an application context. This is an abstract class that the specific application should extend.
# This structure is so that shell.py doesn't have to import something out of the application's core package; instead,
# the Context object in the core extends this class.
# ######################################################################################################################

import os, sqlite3

from multiprocessing import Process
from typing import Type, TYPE_CHECKING

from core.database.zdb import Zdb
from shell.shell import Shell

from flask import Flask, g


# The default context that will be launched by the shell. Set _default_context_name before launching the application.
_default_context_name = None
_default_context_instance = None


class ShellContext:

    def __init__(self, shell: Shell, port: int = None, dir_static: str = None, dir_templates: str = None,
                 db_sql: str = None, db_object: str = None):
        """
        Construct a context for this application and initialize the application.
        :param shell: The CuteWorks shell hosting this application.
        :param port: The port to listen on. Looks to environment variables if not defined.
        :param dir_static: The static files directory. Defaults to the project root's /static directory.
        :param dir_templates: The template files directory. Defaults to the project root's /templates directory.
        :param db_sql: The name of the SQL database. Defaults from environment.
        :param db_object: The name of the object database. Defaults from environment.
        """
        self.shell = shell
        self.running = False

        self._process = None

        # Verify any environment variables that we need.
        if not self.init_env_verify():
            print("Missing required environment variable.")
            quit(1)

        # Set up the context based on parameters, and set defaults for context variables that might not be set.
        if port is None:
            port = int(self.shell.env_get("DEFAULT_PORT"))

        if dir_templates is None:
            dir_templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../templates")

        if dir_static is None:
            dir_static = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../static")

        if db_sql is None:
            db_sql = self.shell.env_get("DEFAULT_SQL_DATABASE")

        if db_object is None:
            db_object = self.shell.env_get("DEFAULT_OBJECT_DATABASE")

        self._port = port
        self._db_sql = db_sql
        self._db_object = db_object

        # Set Flask variables on this object for configuration, set up a reference to the Flask application, set
        # instance variables for Flask, and create the Flask object based on the configuration variables we set on this
        # object.
        self.DEBUG = self.shell.env_get("DEBUG")
        self.SALT = self.shell.env_get("SALT")
        self.SECRET_KEY = self.shell.env_get("SECRET_KEY")

        # Set our own instance variables.
        self._flask_app = Flask(__name__,
                                static_folder=dir_static,
                                template_folder=dir_templates)
        self._flask_app.config.from_object(self)
        self._flask_app.before_first_request(self.request_before_first)
        self._flask_app.before_request(self.request_before)
        self._flask_app.teardown_request(self.request_teardown)

        # Set up singleton fields.
        self._zdb = None

        # Set up routes for Flask.
        self.init_routes(self._flask_app)

    # region Initialization

    def init_env_verify(self):
        """
        Check that the required environment variables are present.
        :return: False if we are missing an environment variable, True otherwise.
        """
        return self.shell.env_expect([
            "DEFAULT_PORT",
            "SALT",
            "SECRET_KEY",
            "DEFAULT_SQL_DATABASE",
            "DEFAULT_OBJECT_DATABASE",
        ])

    def init_routes(self, flask_app):
        """
        Initializes the default routes for the application with the specified Flask application object. The specific
        application's Context object should override init_routes and specify routes directly on the provided Flask
        object.
        :param flask_app: The Flask instance in which to set routes.
        """
        pass

    # endregion

    # region Application control

    def start(self):
        """
        Starts this process running with the application-defined behavior in _start_impl. This should usually start the
        Flask application.
        """
        self.running = True
        self._process = Process(target=self._start_impl)
        self._process.start()

    def _start_impl(self):
        """
        The target for the context's start method. Should be implemented by the application context object.
        """
        pass

    def stop(self):
        """
        Trigger any shutdown requirements and terminate the process hosting this context.
        """
        self.running = False
        self._process.terminate()

    # endregion

    # region Singletons

    def singleton_request_init(self):
        """
        Set up the singletons on the request object so they accessible in the Flask context.
        """
        g.s = lambda: None

        g.s.shell = self.shell
        g.s.context = self

        # The context object (this one) should have methods to get the following singletons. We'll expose them on g.s
        # for ease of access.
        g.s.zdb = self.singleton_get_zdb()

    def singleton_get_zdb(self) -> Zdb:
        """
        Gets the object database associated with the context.
        :return: The object database associated with the context.
        """
        return self._zdb

    def singleton_set_zdb(self, zdb: Zdb) -> None:
        """
        Sets the object database associated with the context.
        :param zdb: The object database to use as the singleton.
        """
        self._zdb = zdb

    # endregion

    # region Global Flask handlers

    def request_before_first(self):
        """
        Any one-time initialization that we want to run only once when the application context starts. When using the
        werkzeug reloader, main will run twice because we're being spawned in a subprocess. This can causes locking
        issues, so possibly only initialize sensitive objects when we're actually ready to process the first request.
        At this point, the database connection is not yet open, so we don't want to attempt any accesses to the DB.
        """

        # Initialize the object database.
        self.singleton_set_zdb(Zdb(self._db_object))

    def request_before(self):
        """
        Do any bringup for things that we need during a request, like setting up the singleton references.
        """
        g.db = self.db_sql_connect()
        self.singleton_request_init()

    def request_teardown(self, exception: BaseException) -> None:
        """
        Take care of any teardown after a request.
        """
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()

    # endregion

    # region Database

    def db_sql_connect(self) -> sqlite3.Connection:
        """
        Connect to the SQL database in order to insert the schema.
        :return: The connection object.
        """
        return sqlite3.connect(self._db_sql)


    # endregion


def default_context_set(default_context_name: Type(ShellContext)) -> None:
    """
    Sets the default context that will be launched.
    :param default_context_name: The default context object type for the application.
    """
    global _default_context_name
    _default_context_name = default_context_name


def default_context_get() -> ShellContext:
    """
    If the default context has been initialized (via the default_context_create) method, return the context instance.
    :return: The instance of the default context.
    """
    return _default_context_instance


def default_context_create(shell: Shell, port: int = None, dir_static: str = None, dir_templates: str = None,
                           db_sql: str = None, db_object: str = None) -> ShellContext:
    """
    Using the default context class, initialize the default context and return it as a reference. Does not invoke .start
    on the context, only initializes it.
    :param shell: The CuteWorks shell hosting this application.
    :param port: The port to listen on. Looks to environment variables if not defined.
    :param dir_static: The static files directory. Defaults to the project root's /static directory.
    :param dir_templates: The template files directory. Defaults to the project root's /templates directory.
    :param db_sql: The name of the SQL database. Defaults from environment.
    :param db_object: The name of the object database. Defaults from environment.
    """
    global _default_context_instance, _default_context_name  # Don't need 2nd one but it helps the type checker.
    _default_context_instance = _default_context_name(shell, port, dir_static, dir_templates, db_sql, db_object)
