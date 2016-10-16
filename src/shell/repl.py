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
            self.cmd_exit()
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

    def cmd_exit(self):
        """
        Exit the REPL and terminate any subprocesses that we spawened.
        :return:
        """
        i = len(self.get_shell().context_get_raw())
        while i > 0:
            i = i - 1
            self.get_shell().context_get_raw()[i].stop()
            self.get_shell().context_remove(i)

        self.running = False

    def cmd_status(self, cmd_ary):
        """
        The status command shows the current status of all application contexts.
        :param cmd_ary: The full command array.
        """

        ctx_idx = 0
        for context in self.get_shell().context_get_raw():
            print(str(ctx_idx) + " - " + ("Active" if context.running else "Ready") + " - :" + str(context._port))
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

        port = input("Port: ")
        sql_database = input("SQL database: ")
        object_database = input("Object database: ")

        # Set defaults here instead of letting the context constructor set them so we can check against existing
        # contexts.
        if port == "":
            port = self.get_shell().env_get("DEFAULT_PORT")

        if sql_database == "":
            sql_database = self.get_shell().env_get("DEFAULT_SQL_DATABASE")

        if object_database == "":
            object_database = self.get_shell().env_get("DEFAULT_OBJECT_DATABASE")

        try:
            port = int(port)
        except ValueError:
            port = ""

        # Make sure this context wouldn't be running on the same port or with any of the same database.
        for ctx in self.get_shell().context_get_raw():
            if ctx._port == port:
                self.get_shell().print_error("A context with this port already exists: " + str(port))
                return
            if ctx._sql_database == sql_database:
                self.get_shell().print_error("A context with this SQL database already exists: " + sql_database)
                return
            if ctx._object_database == object_database:
                self.get_shell().print_error("A context with this object database already exists: " + object_database)
                return

        # TODO: Maybe if the DB/ZDB doesn't exist, run a basic init.

        context = Context(self.get_shell(), port, sql_database, object_database)
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

        self.get_shell().context_start(ctx_idx)

        self.cmd_status([])

    def cmd_context_stop(self, cmd_ary):
        """
        Shuts down a context completely and removes it from the list of contexts.
        :param cmd_ary: The full command array.
        """
        if len(cmd_ary) < 3:
            return

        try:
            idx = int(cmd_ary[2])
        except ValueError:
            return

        self.get_shell().context_stop(idx)
        self.get_shell().context_remove(idx)

        self.cmd_status([])
