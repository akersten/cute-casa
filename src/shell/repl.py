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
            self.show_help(cmd_ary)
            return

        if cmd_base == "a":
            for s in self.get_shell()._contexts:
                print(s)


    def show_help(self, cmdAry):
        """
        Shows help for a command or available commands if no command is specified.
        :param: cmdAry The full command array.
        """

        if len(cmdAry) == 1:
            # General help (just the "?"), show available commands.
            print("Available commands: ?, context")
