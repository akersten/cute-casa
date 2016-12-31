# ######################################################################################################################
# CuteWorks applications have a shell, through which things like the object database can be accessed from outside of
# the Flask routes. The shell should be one of the first things initialized for an application.
# ######################################################################################################################

import os
import random
import math
import sqlite3

from multiprocessing import Process
from threading import Thread
from typing import Type, List, Union

from flask import Flask, g

from core.database.zdb import Zdb
from shell.repl import Repl
from shell.manifest import Manifest

# The CuteWorks string is used for prefixing environment variables.
CUTEWORKS = "CUTEWORKS"
CUTESHELL_VERSION = "0.0.0.0"

# Inspirational strings that may be displayed at startup.
INSPIRATIONS = [
    "Is it perfect, in our little shell?",
]

# When we print the values of the environment variables after loading them, don't display anything in this list.
ENV_SENSITIVE_VARIABLES = [
    "SALT",
    "PASSWORD",
    "SECRET_KEY",
]

# These variables should be interpreted as booleans if they are set as an environment variable.
ENV_BOOLEANS = [
    "DEBUG",
]

# The environment variables that we expect to see set by the run script (at least at this point in the setup; we
# check on an as-needed basis for more specific variables (like default database paths) when we actually set up the
# application context.
ENV_EXPECTED = [
    "DEBUG",
]

# The default context that will be launched by the shell. Set _default_context_name before launching the application.
_default_context_name = None
_default_context_instance = None


class Shell:
    """
    The main shell object that launches the application, initiates the user shell, and tracks singletons.
    """

    def __init__(self, manifest: Manifest):
        """
        Initialize an application context for a CuteWorks application.
        :param manifest: An instance of the CuteManifest object describing the application.
        """
        self.manifest = manifest

        self._contexts = []
        self._env = {}
        self._env_expected = set()
        self._count_errors = 0
        self._count_warnings = 0

        os.system("clear")
        print("CuteShell " + CUTESHELL_VERSION + " initializing...\n")
        print_italic(get_inspiration() + "\n")

        print("\t" + self.manifest.name)
        print("\t" + self.manifest.version)

        print("\nReading environment variables...")
        self.env_init()

        self.env_expect(ENV_EXPECTED)

        print("\nInitializing REPL...")
        self._repl = Repl(self)

    # region Context

    def context_create(self, port: int = None, dir_static: str = None, dir_templates: str = None, db_sql: str = None,
                       db_object: str = None) -> 'ShellContext':
        """
        Creates an instance of the default context with the specified parameters, using this shell.
        :param port: The port to listen on. Looks to environment variables if not defined.
        :param dir_static: The static files directory. Defaults to the project root's /static directory.
        :param dir_templates: The template files directory. Defaults to the project root's /templates directory.
        :param db_sql: The name of the SQL database. Defaults from environment.
        :param db_object: The name of the object database. Defaults from environment.
        :return The ShellContext that was created.
        """
        global _default_context_name
        return _default_context_name(self, port, dir_static, dir_templates, db_sql, db_object)

    def context_add(self, context: 'ShellContext') -> None:
        """
        Adds a context to this shell's list of contexts that can be inspected by the command line operations.
        :param context: The context to add.
        """
        self._contexts.append(context)

    def context_remove(self, context_idx: int) -> None:
        """
        Removes a context from this shell's list of contexts. Assumes that the context in question has already been
        properly shut down and is no longer active; there will be no way of accessing it via the shell after this call.
        :param context_idx: The context number to remove.
        """
        if type(context_idx) is not int:
            raise TypeError("Context index must be an integer.")

        if context_idx >= len(self._contexts) or context_idx < 0:
            return

        del self._contexts[context_idx]

    def context_start(self, context_idx: int) -> None:
        """
        Start a context's host process.
        :param context_idx: The context number to start.
        """
        if type(context_idx) is not int:
            raise TypeError("Context index must be an integer.")

        if len(self._contexts) <= context_idx or context_idx < 0:
            return

        # Start this context - internally, it will create a new process to track its state and console output.
        self._contexts[context_idx].start()

    def context_stop(self, context_idx: int) -> None:
        """
        Stop a context's host process.
        :param context_idx: The context number to stop.
        """
        if type(context_idx) is not int:
            raise TypeError("Context index must be an integer.")

        if len(self._contexts) <= context_idx or context_idx < 0:
            return

        self._contexts[context_idx].stop()

    def context_get_raw_list(self) -> List['ShellContext']:
        """
        Get the raw list backing the context array. Shouldn't use this too often, mostly used from the REPL where we
        want to do things like inspect the list directly.
        :return: The private list of contexts.
        """
        return self._contexts

    def context_get(self, context_idx: int) -> 'ShellContext':
        """
        Gets the object representing the context.
        :param context_idx: The number of the context to get.
        :return: The object representing this context.
        """
        if len(self._contexts) <= context_idx:
            return None

        return self._contexts[context_idx]

    # endregion

    # region Environment

    def env_init(self) -> None:
        """
        Loads any environment variables that start with "CUTEWORKS_" + manifest.env_prefix + "_" and puts them into the
        environment variable dictionary for the context. The environment variables dictionary will have the environment
        variables without any prefix.
        """
        key_prefix = CUTEWORKS + "_" + self.manifest.env_prefix + "_"
        for v in sorted(os.environ):
            if v.startswith(key_prefix):
                key = v[len(key_prefix):]
                val = os.environ[v]

                if key not in ENV_SENSITIVE_VARIABLES:
                    print("\t" + key + "=" + val)
                else:
                    print_italic("\t" + key)

                # Do any necessary casting.
                if key in ENV_BOOLEANS:
                    val = True if val in ['True', 'true', '1', 'yes'] else False

                self._env[key] = val

    def env_get(self, key: str) -> str:
        """
        Gets an environment variable related to the application (i.e. one starting with this application's prefix).
        :param key: The name of the application environment variable to return.
        :return: The value of the environment variable, or None if no such variable is set.
        """

        # Check if we've "expected" this key - if not, we're not really in a safe situation to be getting it, since it
        # has not yet been enforced that this key actually exists in the environment. Emit a warning.
        if key not in self._env_expected:
            self.print_warning("Using unexpected application environment variable '" + key + "'.")

        if key not in self._env:
            return None
        return self._env[key]

    def env_expect(self, keys: Union[str, List[str]]) -> bool:
        """
        Checks if a list of keys or a single key exists in the environment.
        :param keys: The key or list of keys to check.
        :return: True if all specified keys exist in the environment, False if any don't.
        """
        if type(keys) is list:
            for key in keys:
                if key not in self._env:
                    print_red("\t" + key)
                    return False
                self._env_expected.add(key)
        else:
            if keys not in self._env:
                print_red("\t" + keys)
                return False
            self._env_expected.add(keys)

        return True

    # endregion

    # region Control flow

    def start(self) -> None:
        """
        The main entry point for the shell after it has been initialized. This will drop the user into a REPL and allow
        them to launch the application. Maybe in the future this can be used to reload environment variables or similar,
        if we exit out of the application context/REPL and want to relaunch without restarting the program.
        """

        # If we're in debug mode, Flask will run with a stat/restarter and that will completely bork our repl/subprocess
        # scheme. Just run it as a single standalone app in debug mode, with the assumed defaults.
        if self.env_get("DEBUG"):
            print_red("Running in standalone debug mode.")

            if default_context_get():
                print_red("Default context already exists.")
                return

            default_context_set(self.manifest.default_context)
            default_context_create(self)
            _default_context_instance.start()
            return

        user_input = ""
        while user_input.lower() != "exit":
            print("\n\t`repl` -> Launch REPL\n\t`exit` -> Exit Shell\n")
            user_input = input("cuteshell $ ")

            if len(user_input) == 0:
                continue

            if user_input == "repl":
                t = Thread(target=self._repl.run)
                t.start()
                t.join()

    # endregion

    def print_error(self, message: str) -> None:
        """
        Prints an error message - in the future, we might log this error somewhere to the shell error log.
        :param message: The message to print.
        """
        self._count_errors += 1
        print_red(message)

    def print_warning(self, message: str) -> None:
        """
        Prints a warning message - in the future, we might log this warning somewhere to the shell warning log.
        :param message: The message to print.
        """
        self._count_warnings += 1
        print_yellow(message)


class ShellContext:
    """
    The shell launches an application context. This is an abstract class that the specific application should extend.
    This structure is so that shell.py doesn't have to import something out of the application's core package; instead,
    the Context object in the core extends this class.
    """

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

        self._requests_issued = 0
        self._requests_completed = 0
        self._requests_in_flight = 0
        self._requests_failed = 0

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

    def init_env_verify(self) -> bool:
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

    def init_routes(self, flask_app: Flask) -> None:
        """
        Initializes the default routes for the application with the specified Flask application object. The specific
        application's Context object should override init_routes and specify routes directly on the provided Flask
        object.
        :param flask_app: The Flask instance in which to set routes.
        """
        pass

    # endregion

    # region Inspection

    def get_port(self) -> int:
        """
        Gets the port number that this application runs on.
        :return: The port number for this application.
        """
        return self._port

    def db_sql_get(self) -> str:
        """
        Gets the path of the SQL database.
        :return: The path to the SQL database.
        """
        return self._db_sql

    def db_object_get(self) -> str:
        """
        Gets the path of the object database.
        :return: The path to the object database.
        """
        return self._db_object

    # endregion

    # region Application control

    def start(self) -> None:
        """
        Starts this process running with the application-defined behavior in _start_impl. This should usually start the
        Flask application.
        """
        self.running = True
        self._process = Process(target=self._start_impl)
        self._process.start()

    def _start_impl(self) -> None:
        """
        The target for the context's start method. Should be implemented by the application context object.
        """
        pass

    def stop(self) -> None:
        """
        Trigger any shutdown requirements and terminate the process hosting this context.
        """
        self.running = False
        self._process.terminate()

    # endregion

    # region Singletons

    def singleton_request_init(self) -> None:
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

    def request_before_first(self) -> None:
        """
        Any one-time initialization that we want to run only once when the application context starts. When using the
        werkzeug reloader, main will run twice because we're being spawned in a subprocess. This can causes locking
        issues, so possibly only initialize sensitive objects when we're actually ready to process the first request.
        At this point, the database connection is not yet open, so we don't want to attempt any accesses to the DB.
        """

        # Initialize the object database.
        self.singleton_set_zdb(Zdb(self._db_object))

    def request_before(self) -> sqlite3.Connection:
        """
        Do any bringup for things that we need during a request, like setting up the singleton references.
        """
        self._requests_issued += 1
        self._requests_in_flight += 1

        g.db = self.db_sql_connect()
        self.singleton_request_init()

    def request_teardown(self, exception: BaseException) -> None:
        """
        Take care of any teardown after a request.
        :param exception: Any exception that occurred during the processing of this request.
        """
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()

        self._requests_in_flight -= 1
        if exception:
            self._requests_failed += 1
        else:
            self._requests_completed += 1

    # endregion

    # region Database

    def db_sql_connect(self) -> sqlite3.Connection:
        """
        Connect to the SQL database in order to insert the schema.
        :return: The connection object.
        """
        return sqlite3.connect(self._db_sql)

    # endregion


# ######################################################################################################################
# Static functions to implement shell functionality.
# ######################################################################################################################

# region Printing

def print_italic(line: str) -> None:
    """
    Try to print a line in italics.
    :param line: The line to print.
    """
    if os.name == "posix":
        # Hopefully Bash or other emulator that understands this formatting.
        os.system("echo -e \"\\e[3m" + line + "\\e[0m\"")
    else:
        # Probably won't understand the formatting.
        print(line)


def print_bold(line: str) -> None:
    """
    Try to print a line in bold.
    :param line: The line to print.
    """
    if os.name == "posix":
        os.system("echo -e \"\\e[1m" + line + "\\e[0m\"")
    else:
        print(line)


def print_red(line: str) -> None:
    """
    Try to print a line in red.
    :param line: The line to print.
    """
    if os.name == "posix":
        os.system("echo -e \"\\e[31m" + line + "\\e[0m\"")
    else:
        print(line)


def print_yellow(line: str) -> None:
    """
    Try to print a line in yellow.
    :param line: The line to print.
    """
    if os.name == "posix":
        os.system("echo -e \"\\e[33m" + line + "\\e[0m\"")
    else:
        print(line)

# endregion


# region Default context

def default_context_set(default_context_name: 'Type(ShellContext)') -> None:
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
    global _default_context_instance, _default_context_name
    _default_context_instance = _default_context_name(shell, port, dir_static, dir_templates, db_sql, db_object)

# endregion


# Region Miscellaneous

def get_inspiration():
    """
    Returns an inspirational phrase to display during shell initialization.
    :return: An inspirational phrase from the inspirations array.
    """
    return INSPIRATIONS[math.floor(random.random() * len(INSPIRATIONS))]

# endregion
