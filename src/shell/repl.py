# ######################################################################################################################
# This REPL is launched by the shell to accept input once the program launches.
# ######################################################################################################################

REPL_PROMPT = "cute $ "  # The REPL prompt that the user will see.


class Repl:
    """
    The REPL for the CuteWorks application. Should be launched as a thread by the main shell.
    """

    def __init__(self, shell):
        self._shell = shell

        # The function pointer dictionary containing the list of commands that
        self._commands = {
            "status": self.cmd_status,
            "context": self.cmd_context
        }

        self.running = False

    def run(self):
        self.running = True

        while self.running:
            cmd = self.prompt()
            self.eval(cmd)

    def get_shell(self):
        """
        Returns a reference to the shell (that has application contexts), which this REPL is running within.
        :return: The Shell object reference.
        """
        return self._shell


    def prompt(self) -> str:
        """
        Show the shell prompt and read the user input. If the user input is well-formed, return it. Otherwise continue
        to prompt.
        :return: A well-formed user input.
        """
        user_input = ""
        while user_input == "":
            user_input = input(REPL_PROMPT)
            if user_input == "":
                continue
        return user_input


    def eval(self, cmd: str):
        """
        Execute user input received after prompting. The input probably needs to be parsed.
        :param cmd: The raw user input to evaluate.
        """
        cmd = cmd.strip()
        cmd_ary = cmd.split()

        if len(cmd_ary) == 0:
            return

        cmd_base = cmd_ary[0].lower()

        if cmd_base == "exit":
            self.running = False
            return

        if cmd_base == "?":
            self.show_help()
            return

        if cmd_base in self._commands.keys():
            self._commands[cmd_base](cmd_ary)
            return

    def show_help(self):
        """
        Shows help for  available commands.
        """
        print("Available commands:")
        for cmd in self._commands.keys():
            print("\t" + cmd)

    def cmd_status(self, cmd_ary):
        """
        The status command shows the current status of all application contexts.
        :param cmd_ary: The full command array.
        """

        if len(cmd_ary) == 1:
            print("There are " + str(len(self.get_shell().context_get_raw())) + " contexts")

    def cmd_context(self, cmd_ary):
        """
        The context command controls the behavior of individual application contexts (starting, stopping, status, etc.).
        :param cmd_ary: The full command array.
        """
        if len(cmd_ary) == 1:
            print("The context command controls the behavior of individual application contexts. Usage:")
            print("\tcontext create - Creates a new context.")
            print("\tcontext start  - Starts a context.")
            print("\tcontext stop   - Stops a context.")
            return
