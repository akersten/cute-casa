# ######################################################################################################################
# This REPL is launched by the shell to accept input once the program launches.
# ######################################################################################################################

from core.context import Context

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

        ctx_idx = 0
        for context in self.get_shell().context_get_raw():
            print(str(ctx_idx) + " - " + ("Active" if context.running else "Ready") + " - :"  + str(context.port))
            ctx_idx += 1

    def cmd_context(self, cmd_ary):
        """
        The context command controls the behavior of individual application contexts (starting, stopping, status, etc.).
        :param cmd_ary: The full command array.
        """
        if len(cmd_ary) <= 1:
            print("The context command controls the behavior of individual application contexts. Usage:")
            print("\tcontext create - Creates a new context.")
            print("\tcontext start  - Starts a context.")
            print("\tcontext stop   - Stops a context.")
            return

        sub_cmd = cmd_ary[1].lower()

        if sub_cmd == "create":
            self.cmd_context_create(cmd_ary)

        if sub_cmd == "start":
            self.cmd_context_start(cmd_ary)

        if sub_cmd == "stop":
            self.cmd_context_stop(cmd_ary)


    def cmd_context_create(self, cmd_ary):
        """
        Creates a context for this application and adds it to the shell.
        :param cmd_ary: The full command array.
        """
        if len(self.get_shell().context_get_raw()) == 1:
            print(
                    """
                    Sorry, support for more than one context isn't implemented yet. At a minimum, the framework for multiple
                    databases will need to be put in place (as well as initialization code for creating them).
                    """
            )
            return

        context = Context(self.get_shell())
        self.get_shell().context_add(context)

        self.cmd_status([])

    def cmd_context_start(self, cmd_ary):
        """
        Brings up a context and causes it to run.
        :param cmd_ary: The full command array.
        """
        if len(cmd_ary) < 3:
            return

        try:
            ctx_idx = int(cmd_ary[2])
        except ValueError:
            return

        contexts = self.get_shell().context_get_raw()

        if len(contexts) <= ctx_idx:
            print("Context does not exist: " + str(ctx_idx))
            return

        # TODO: This should be in a subprocess so we can (a) redirect stdout to a log for interactive viewing and (b)
        # run in debug mode.
        contexts[ctx_idx].start()

        self.cmd_status([])

    def cmd_context_stop(self, cmd_ary):
        """
        Shuts down a context completely and removes it from the list of contexts.
        :param cmd_ary: The full command array.
        """
        pass