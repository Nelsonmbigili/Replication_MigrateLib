import plac

from venvs import converge, create, find, remove, temporary


def main(command: str):
    """
    Centralized virtual environments.
    """
    commands = {
        'converge': converge.main,
        'create': create.main,
        'find': find.main,
        'remove': remove.main,
        'temporary': temporary.main,
    }
    
    if command in commands:
        commands[command]()
    else:
        print("Available commands: ", ', '.join(commands.keys()))


if __name__ == '__main__':
    plac.call(main)
