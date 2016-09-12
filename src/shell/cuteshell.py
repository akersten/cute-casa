# ######################################################################################################################
# CuteShell core functions and platform-specific implementations go here.
# ######################################################################################################################

import os


def print_italic(line):
    if os.name == "posix":
        # Hopefully Bash or other emulator that understands this formatting.
        os.system("echo -e \"\\e[3m" + line + "\\e[0m\"")
    else:
        # Probably won't understand the formatting.
        print(line)


def print_bold(line):
    if os.name == "posix":
        os.system("echo -e \"\\e[1m" + line + "\\e[0m\"")
    else:
        print(line)
