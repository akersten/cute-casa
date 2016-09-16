# ######################################################################################################################
# CuteWorks applications have a shell, through which things like the object database can be accessed from outside of
# the Flask routes. The shell should be one of the first things initialized for an application.
# ######################################################################################################################

import os
import random
import math


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

    def __init__(self, manifest):
        """
        Initialize an application context for a CuteWorks application.
        :param manifest: An instance of the CuteManifest object describing the application.
        """
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

        self._contexts = []

    def context_add(self, context):
        """
        Adds a context to this shell's list of contexts that can be inspected by the command line operations.
        :param context: The context to add.
        """
        self._contexts.append(context)

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