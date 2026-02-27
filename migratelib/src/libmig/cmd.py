from subprocess import Popen, PIPE

cmd = {
    "default_print": print
}


def run(args: list[any], cwd=None, write=None):
    """
    Run a command in the shell.
    :param args: The command to run.
    :param cwd: The directory in which to run the command.
    :param write: The function to use to write output. Default is print.
    """
    write = write or cmd["default_print"]
    process = Popen(args, cwd=cwd, stdout=PIPE, text=True, encoding="utf-8")
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            write(output.strip())
    rc = process.poll()
    return rc


def run_and_get_output(args: list[any], cwd=None):
    """
    Run a command in the shell and get the output.
    :param args: The command to run.
    :param cwd: The directory in which to run the command.
    :return: The output of the command.
    """
    process = Popen(args, cwd=cwd, stdout=PIPE, text=True, encoding="utf-8")
    output, _ = process.communicate()
    return output
