import json
import sys

import pkg_resources
from rich.console import Console
from rich.table import Table

from dundie import core


def main(*args):
    """Dunder Mifflin Rewards System.

    This CLI application controls Dunder Mifflin rewards.

    - Admins can load information to the people database and assign points.
    - Users can view reports and transfer points.

    """
    if "--version" in args:
        print(pkg_resources.get_distribution("dundie").version)
        return

    if len(args) == 0 or args[0] not in {"load", "show", "add", "remove"}:
        print("Usage: main [command] [options]")
        print("Commands: load, show, add, remove")
        return

    command = args[0]
    command_args = args[1:]

    if command == "load":
        plac_call(load, command_args)
    elif command == "show":
        plac_call(show, command_args)
    elif command == "add":
        plac_call(add, command_args)
    elif command == "remove":
        plac_call(remove, command_args)


def load(filepath: ("Path to the file", "positional")):
    """Loads the file to the database.

    ## Features

    - Validates data
    - Parses the file
    - Loads to database
    """
    table = Table(title="Dunder Mifflin Associates")
    headers = ["email", "name", "dept", "role", "currency", "created"]
    for header in headers:
        table.add_column(header, style="magenta")

    result = core.load(filepath)
    for person in result:
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)


def show(
    dept: ("Department to filter by", "option", None) = None,
    email: ("Email to filter by", "option", None) = None,
    output: ("Output file path", "option", None) = None,
):
    """Shows information about user or dept."""
    query = {"dept": dept, "email": email}
    result = core.read(**query)
    if output:
        with open(output, "w") as output_file:
            output_file.write(json.dumps(result))

    if len(result) == 0:
        print("Nothing to show")
        return

    table = Table(title="Dunder Mifflin Report")
    for key in result[0]:
        table.add_column(key.title().replace("_", " "), style="magenta")

    for person in result:
        person["value"] = f"{person['value']:.2f}"
        person["balance"] = f"{person['balance']:.2f}"
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)


def add(
    value: ("Points to add", "positional", int),
    dept: ("Department to filter by", "option", None) = None,
    email: ("Email to filter by", "option", None) = None,
):
    """Add points to the user or dept."""
    query = {"dept": dept, "email": email}
    core.add(value, **query)
    show(dept=dept, email=email)


def remove(
    value: ("Points to remove", "positional", int),
    dept: ("Department to filter by", "option", None) = None,
    email: ("Email to filter by", "option", None) = None,
):
    """Removes points from the user or dept."""
    query = {"dept": dept, "email": email}
    core.add(-value, **query)
    show(dept=dept, email=email)


if __name__ == "__main__":
    import plac

    plac.call(main)
