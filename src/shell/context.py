# ######################################################################################################################
# CuteWorks applications have a context, through which things like the object database can be accessed from outside of
# the Flask routes. Application variables are set here. The context should be one of the first things initialized for an
# application.
# ######################################################################################################################

import os
import random
import math

from shell.cuteshell import print_italic


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


class Context:
    """
    The main context object that launches the application, initiates the user shell, and tracks singletons.
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
        self.init_env()

    def init_env(self):
        """
        Loads any environment variables that start with "CUTEWORKS_" + manifest.env_prefix and puts them into the
        environment variable dictionary for the context. The environment variables dictionary will have the environment
        variables without any prefix.
        """
        for v in sorted(os.environ):
            if v.startswith(CUTEWORKS + "_" + self.manifest.env_prefix):
                key = v[len(CUTEWORKS + "_" + self.manifest.env_prefix):]
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

    def get_env(self, key):
        """
        Gets an environment variable related to the application (i.e. one starting with this application's prefix).
        :param key: The name of the application environment variable to return.
        :return: The value of the environment variable, or None if no such variable is set.
        """
        if key not in self._env:
            return None
        return self._env[key]
