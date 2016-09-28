# ######################################################################################################################
# The CuteCasa application bootstrapper & entry point. Sets up the application context and starts the Flask engine. Run
# this via cute.sh so that environment variables are set for the context.
# ######################################################################################################################

from core.context import Context

from shell.shell import Shell
from shell.manifest import Manifest

from flask import Flask


# ######################################################################################################################
# First, set up the application shell and read configuration from environment variables set in the secret shell script
# that we don't commit. Then, set some Flask configuration variables that get read from this namespace, and create the
# Flask application with the appropriate request handlers and hooks.
#
# There is one shell object that can host multiple application contexts within it.
# ######################################################################################################################

APP_TITLE = "CuteCasa"
APP_VERSION = "0.0.0"
APP_PREFIX = "CUTECASA"

DIR_TEMPLATES = "../templates"
DIR_STATIC = "../static"

# ######################################################################################################################
# Initialize and spawn the application shell.
# ######################################################################################################################

shell = Shell(Manifest(APP_TITLE, APP_VERSION, APP_PREFIX))
context = Context(shell, Flask(__name__, template_folder=DIR_TEMPLATES, static_folder=DIR_STATIC))
shell.context_add(context)

shell.start()
