# ######################################################################################################################
# This REPL is launched by the shell to accept input once the program launches.
# ######################################################################################################################


REPL_PROMPT = "cute $ " # The REPL prompt that the user will see.


class Repl:
    """
    The REPL for the CuteWorks application. Should be launched as a thread by the main shell.
    """


    def __init__(self):
        self.running = False
        pass


    def run(self):
        self.running = True

        while self.running:
            cmd = self.prompt()
            self.eval(cmd)


    def prompt(self) -> str:
        """
        Show the shell prompt and read the user input. If the user input is well-formed, return it. Otherwise continue
        to prompt.
        :return: A well-formed user input.
        """
        userInput = ""
        while userInput == "":
            userInput = input(REPL_PROMPT)
            if userInput == "":
                continue
        return userInput


    def eval(self, cmd: str):
        """
        Execute user input received after prompting. The input probably needs to be parsed.
        :param cmd: The raw user input to evaluate.
        """
        cmd = cmd.strip()
        cmdAry = cmd.split()

        if len(cmdAry) == 0:
            return

        cmdBase = cmdAry[0].lower()

        if cmdBase == "exit":
            self.running = False
            return
