# ######################################################################################################################
# The manifest for a CuteWorks application describes things about that application, like its title, version, and prefix
# for environment variables.
# ######################################################################################################################

from shell.shellContext import ShellContext

class Manifest:

    def __init__(self, name: str, version: str, env_prefix: str, default_context: ShellContext) -> None:
        """
        Creates the manifest for a CuteWorks application.
        :param name: The name of this application (e.g. "CuteCasa").
        :param version: The version of this application (e.g. "1.0.2.12").
        :param env_prefix: The environment variable prefix for this application (e.g. "CUTECASA").
        """
        self.name = name
        self.version = version
        self.env_prefix = env_prefix
        self.default_context = default_context
