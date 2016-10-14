# ######################################################################################################################
# CuteWorks applications have a shell, through which things like the object database can be accessed from outside of
# the Flask routes. The shell should be one of the first things initialized for an application.
# ######################################################################################################################

import os
import random
import math

from threading import Thread

from core.context import Context
from shell.repl import Repl

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
    "DEBUG"
]


def get_inspiration():
    """
    Returns an inspirational phrase to display during shell initialization.
    :return: An inspirational phrase from the inspirations array.
    """
    return INSPIRATIONS[math.floor(random.random() * len(INSPIRATIONS))]


class Shell:
    """
    The main shell object that launches the application, initiates the user shell, and tracks singletons.
    """

    # region Initialization

    def __init__(self, manifest):
        """
        Initialize an application context for a CuteWorks application.
        :param manifest: An instance of the CuteManifest object describing the application.
        """
        os.system("clear")
        print("CuteShell " + CUTESHELL_VERSION + " initializing...\n")
        print_italic(get_inspiration())

        print("\nLoading manifest for application...")
        self.manifest = manifest
        print("\t" + self.manifest.name)
        print("\t" + self.manifest.version)

        print("\nReading environment variables...")
        self._env = {}
        self._env_expected = set()
        self.env_init()

        print("\nInitializing REPL...")
        self._repl = Repl(self)

        self._contexts = []


    def context_add(self, context):
        """
        Adds a context to this shell's list of contexts that can be inspected by the command line operations.
        :param context: The context to add.
        """
        self._contexts.append(context)

    def context_remove(self, context_idx):
        """
        Removes a context from this shell's list of contexts. Assumes that the context in question has already been
        properly shut down and is no longer active; there will be no way of accessing it via the shell after this call.
        :param context_idx: The context number to remove.
        """
        if context_idx >= len(self._contexts) or context_idx < 0:
            return
        del self._contexts[context_idx]


    def context_get_raw(self):
        """
        Get the raw list backing the context array. Shouldn't use this too often, mostly used from the REPL where we
        want to do things like inspect the list directly.
        :return: The private list of contexts.
        """
        return self._contexts

    def context_get(self, context_idx):
        """
        Gets the object representing the context.
        :param context_idx: The number of the context to get.
        :return: The object representing this context.
        """
        if len(self._contexts) <= context_idx:
            return None
        return self._contexts[context_idx]

    def env_init(self):
        """
        Loads any environment variables that start with "CUTEWORKS_" + manifest.env_prefix and puts them into the
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
                    if val in ['True', 'true', '1', 'yes']:
                        val = True
                    else:
                        val = False

                self._env[key] = val

    def env_get(self, key):
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

    def env_expect(self, keys):
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

    def start(self):
        """
        The main entry point for the shell after it has been initialized. This will drop the user into a REPL and allow
        them to launch the application. Maybe in the future this can be used to reload environment variables or similar,
        if we exit out of the application context/REPL and want to relaunch without restarting the program.
        """

        # If we're in debug mode, Flask will run with a stat/restarter and that will completely bork our repl/subprocess
        # scheme. Just run it as a single standalone app in debug mode, with the assumed defaults.
        if self._env.get("DEBUG"):      # Not using env_get because the context hasn't env_expect'ed anything yet.
            print_red("Running in standalone debug mode.")
            context = Context(self)
            context.start()
            return

        userInput = ""
        while userInput.lower() != "exit":
            print("\n\t`repl` -> Launch REPL\n\t`exit` -> Exit Shell\n")
            userInput = input("cuteshell $ ")

            if len(userInput) == 0:
                continue

            if userInput == "repl":
                t = Thread(target=self._repl.run)
                t.start()
                t.join()

    # endregion

    def print_error(self, message):
        """
        Prints an error message - in the future, we might log this error somewhere to the shell error log.
        :param message: The message to print.
        """
        print_red(message)

    def print_warning(self, message):
        """
        Prints a warning message - in the future, we might log this warning somewhere to the shell warning log.
        :param message: The message to print.
        """
        print_yellow(message)

# ######################################################################################################################
# Static functions to implement shell functionality.
# ######################################################################################################################


def print_italic(line):
    if os.name == "posix":
        # Hopefully Bash or other emulator that understands this formatting.
        os.system("echo -e \"\\e[3m" + line + "\\e[0m\"")
    else:
        # Probably won't understand the formatting.
        print(line)


def print_bold(line):
    if os.name == "posix":
        os.system("echo -e \"\\e[1m" + line + "\\e[0m\"")
    else:
        print(line)


def print_red(line):
    if os.name == "posix":
        os.system("echo -e \"\\e[31m" + line + "\\e[0m\"")
    else:
        print(line)

def print_yellow(line):
    if os.name == "posix":
        os.system("echo -e \"\\e[33m" + line + "\\e[0m\"")
    else:
        print(line)