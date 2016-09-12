# ######################################################################################################################
# CuteWorks applications have a context, through which things like the object database can be accessed from outside of
# the Flask routes. Application variables are set here.
# ######################################################################################################################

import os
import random
import math


CUTEWORKS = "CUTEWORKS"                     # The CuteWorks string, used for prefixing environment variables.
CUTESHELL_VERSION = "0.0.0.0"

inspirations = [
    "Is it perfect, in our little shell?",
]


def get_inspiration():
    """
    Returns an inspirational phrase to display during shell initialization.
    :return: An inspirational phrase from the inspirations array.
    """
    return inspirations[math.floor(random.random() * len(inspirations))]


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
        os.system("echo -e \"\\e[3m" + get_inspiration() + "\\e[0m\"")

        self.manifest = manifest

        self.env = {}
        self.init_env()

    def init_env(self):
        """
        Loads any environment variables that start with "CUTEWORKS_" + manifest.env_prefix and puts them into the
        environment variable dictionary for the context. The environment variables dictionary will have the environment
        variables without any prefix.
        """
        for v in os.environ:
            v = "" + v
            if v.startswith(CUTEWORKS + "_" + self.manifest.env_prefix):
                self.env[v[len(CUTEWORKS + "_" + self.manifest.env_prefix):]] = os.environ[v]
