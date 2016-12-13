# ######################################################################################################################
# CuteWorks applications have a shell, through which things like the object database can be accessed from outside of
# the Flask routes. The shell should be one of the first things initialized for an application.
# ######################################################################################################################

import os
import random
import math

from threading import Thread
from typing import List, Union

import shell.shellContext

from shell.repl import Repl
from shell.manifest import Manifest
from shell.shellContext import ShellContext

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

    def context_add(self, context: ShellContext) -> None:
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

    def context_get_raw_list(self) -> List[ShellContext]:
        """
        Get the raw list backing the context array. Shouldn't use this too often, mostly used from the REPL where we
        want to do things like inspect the list directly.
        :return: The private list of contexts.
        """
        return self._contexts

    def context_get(self, context_idx: int) -> ShellContext:
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
                    if val in ['True', 'true', '1', 'yes']:
                        val = True
                    else:
                        val = False

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

            if shell.shellContext.default_context_get():
                print_red("Default context already exists.")
                return

            shell.shellContext.default_context_set(self.manifest.default_context)
            context = shell.shellContext.default_context_create(self)
            context.start()
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

# ######################################################################################################################
# Static functions to implement shell functionality.
# ######################################################################################################################


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
