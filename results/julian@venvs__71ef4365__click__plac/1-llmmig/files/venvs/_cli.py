import plac

from venvs import converge, create, find, remove, temporary


def main(*args):
    """
    Centralized virtual environments.
    """
    commands = {
        "converge": converge.main,
        "create": create.main,
        "find": find.main,
        "remove": remove.main,
        "temporary": temporary.main,
    }

    if not args or "--help" in args or "-h" in args:
        print("Usage: venvs [COMMAND]")
        print("\nCommands:")
        for command in commands:
            print(f"  {command}")
        print("\nOptions:")
        print("  -h, --help  Show this message and exit.")
        print("  --version   Show the version and exit.")
        return

    if "--version" in args:
        print("venvs, version 8.1.7")
        return

    command = args[0]
    if command in commands:
        plac.Interpreter.call(commands[command], args[1:])
    else:
        print(f"Error: Unknown command '{command}'")
        print("Use -h or --help for usage information.")


if __name__ == "__main__":
    plac.call(main)
