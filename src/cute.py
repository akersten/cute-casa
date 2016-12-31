# ######################################################################################################################
# The CuteCasa application bootstrapper & entry point. Sets up the application context and starts the Flask engine. Run
# this via cute.sh so that environment variables are set for the context.
# ######################################################################################################################

from core.context import Context
from shell.manifest import Manifest
from shell.shell import Shell

# ######################################################################################################################
# First, set up the application shell and read configuration from environment variables set in the secret shell script
# that we don't commit. Then, set some Flask configuration variables that get read from the environment, and create the
# Flask application with the appropriate request handlers and hooks.
#
# There is one shell object that can host multiple application contexts within it.
# ######################################################################################################################

APP_TITLE = "CuteCasa"
APP_VERSION = "0.0.0"
APP_PREFIX = "CUTECASA"

# ######################################################################################################################
# Initialize and spawn the application shell. Point the shell framework to the application's context.
# ######################################################################################################################

shell = Shell(Manifest(APP_TITLE, APP_VERSION, APP_PREFIX, Context))
shell.start()
