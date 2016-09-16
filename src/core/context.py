# ######################################################################################################################
# THe global context for the CuteCasa application. This object tracks the global state and singletons for an instance.
# ######################################################################################################################

from core.web.client import run_integrity_checks
from route import routes

from flask import g

class Context:
    """
    The CuteCasa global context for this instance, to track state and singletons.
    """
    def __init__(self, shell, flaskApp):
        self.shell = shell
        self.flaskApp = flaskApp

        if not self.init_env_verify():
            print("Missing required environment variable.")
            quit(1)

        # Set Flask variables on this object.
        self.DEBUG = self.shell.env_get('DEBUG')
        self.SECRET_KEY = self.shell.env_get('SECRET_KEY')

        # Singleton initialization. TODO: What is this
        self.Zdb = None
        self.Yoer = None

        # Initialize routes and Flask functions..
        flaskApp.config.from_object(self)
        self.init_routes()

        flaskApp.before_first_request(self.before_first_request)
        flaskApp.before_request(self.before_request)
        flaskApp.teardown_request(self.teardown_request)

    # region Initialization

    def init_env_verify(self):
        """
        Check that the required environment variables are present.
        :return: False if we are missing an environment variable, True otherwise.
        """
        return self.shell.env_expect([
            "DEBUG",
            "SECRET_KEY",
            "PORT",
            "SQL_DATABASE",
            "OBJECT_DATABASE",
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
        self.flaskApp.run(host='0.0.0.0', port=int(self.shell.env_get('PORT')))

    # endregion