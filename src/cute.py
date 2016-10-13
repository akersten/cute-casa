# ######################################################################################################################
# The CuteCasa application bootstrapper & entry point. Sets up the application context and starts the Flask engine. Run
# this via cute.sh so that environment variables are set for the context.
# ######################################################################################################################

from shell.shell import Shell
from shell.manifest import Manifest

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

# ######################################################################################################################
# Initialize and spawn the application shell.
# ######################################################################################################################

shell = Shell(Manifest(APP_TITLE, APP_VERSION, APP_PREFIX))
shell.start()
