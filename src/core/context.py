# ######################################################################################################################
# THe global context for the CuteCasa application. This object tracks the global state and singletons for an instance.
# ######################################################################################################################

import os
from multiprocessing import Process

from core.web.client import run_integrity_checks
from route import routes

from flask import Flask, g

class Context:
    """
    The CuteCasa global context for this instance, to track state and singletons.
    """
    def __init__(self, shell, port=None, sql_database=None, object_database=None, dir_static=None, dir_templates=None):
        self.shell = shell
        self.running = False
        self._process = None

        # Set defaults for context variales that might not be set.
        if port is None:
            port = int(self.shell.env_get("DEFAULT_PORT"))

        if sql_database is None:
            sql_database = self.shell.env_get("DEFAULT_SQL_DATABASE")

        if object_database is None:
            object_database = self.shell.env_get("DEFAULT_OBJECT_DATABASE")

        if dir_templates is None:
            dir_templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../templates")

        if dir_static is None:
            dir_static = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../static")


        self._port = port
        self._sql_database = sql_database
        self._object_database = object_database

        if not self.init_env_verify():
            print("Missing required environment variable.")
            quit(1)

        # Set Flask variables on this object.
        self.DEBUG = self.shell.env_get("DEBUG")
        self.SECRET_KEY = self.shell.env_get("SECRET_KEY")
        self.SALT = self.shell.env_get("SALT")

        # Set our own instance variables.
        self.flaskApp = Flask(__name__,
                              static_folder=dir_static,
                              template_folder=dir_templates)


        # Singleton initialization. TODO: What is this
        self.Zdb = None
        self.Yoer = None

        # Initialize routes and Flask functions..
        self.flaskApp.config.from_object(self)
        self.init_routes()

        self.flaskApp.before_first_request(self.before_first_request)
        self.flaskApp.before_request(self.before_request)
        self.flaskApp.teardown_request(self.teardown_request)

    # region Initialization

    def init_env_verify(self):
        """
        Check that the required environment variables are present.
        :return: False if we are missing an environment variable, True otherwise.
        """
        return self.shell.env_expect([
            "SECRET_KEY",
            "SALT"
        ])

    def init_routes(self):
        """
        Set up the routes for this Flask application.
        """

        # TODO: Move these somewhere else where we're not editing context.py all the time.
        self.flaskApp.add_url_rule('/', 'splash', view_func=routes.splash)
        self.flaskApp.add_url_rule('/login', 'login', methods=["GET","POST"], view_func=routes.login)
        self.flaskApp.add_url_rule('/register', 'register', methods=["GET","POST"], view_func=routes.register)


    # endregion

    # region Flask handlers

    def before_first_request(self):
        """
        Any one-time initializatino that we want to run only once when the application context starts. When using the
        werkzeug reloader, main will run twice because we're being spawned in a subprocess. This causes locking issues
        with zodb, so only initialize it when we're actually ready to process the first request.
        """
        #global S_Zdb, S_Yoer

        #g.db = connect_db() # Connect to the SQL database to provide logging functionality.
        #logger.logSystem("First request received, initializing.")

        # Set up dog object's singletons.
        #S_Zdb = zdb.Zdb(context.env_get("OBJECT_DATABASE"))

        #if (S_Zdb.root.globalSettings.yoApiKey is not None and S_Zdb.root.globalSettings.yoApiKey != ""):
        #   S_Yoer = Yoer(S_Zdb.root.globalSettings.yoApiKey)

        #db = getattr(g, 'db', None)
        #if db is not None:
        #   db.close()

    def before_request(self):
        """
        Do any bringup for things that we need during a request.
        """
        g.shell = self.shell
        g.context = self


        # TODO: find better subscripts of g to set things on. These should actually all be accessed via the context
        # anyway so there shouldn't be much to do here. THis context object should have instance methods like get_db()
        # or similar to get these things. We would just have to do the connecting to the database here using the local
        # reference we already have.
        #g.db = connect_db()

        # Add singleton references to dog object.
        g.dog = lambda: None
        #g.dog.zdb = S_Zdb
        #g.dog.yoer = S_Yoer


        #run_integrity_checks()

    def teardown_request(self, exception):
        """
        Take care of any teardown after a request.
        """
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()

    # endregion

    # region Application control

    def start(self):
        self.running = True
        self._process = Process(target=self._start_impl)
        self._process.start()

    def _start_impl(self):
        """
        The target for context process launch - starts the Flask application.
        """
        self.flaskApp.run(host='0.0.0.0', port=self._port)

    def stop(self):
        """
        Trigger any shutdown requirements and terminate the process hosting this context.
        """
        self.running = False
        self._process.terminate()

    # endregion