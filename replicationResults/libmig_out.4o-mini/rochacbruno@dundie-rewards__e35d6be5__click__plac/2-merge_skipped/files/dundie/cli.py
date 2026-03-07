import json

import pkg_resources
import plac
from rich.console import Console
from rich.table import Table

from dundie import core

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True


@click.group()
@click.version_option(pkg_resources.get_distribution("dundie").version)
def main():
    """Dunder Mifflin Rewards System.

    This cli application controls Dunder Mifflin rewards.

    - admins can load information to the people database and assign points.
    - users can view reports and transfer points.

    """
    plac.call(load, '--filepath', type=str)
    plac.call(show, '--dept', required=False, '--email', required=False, '--output', default=None)
    plac.call(add, 'value', type=int, required=True, '--dept', required=False, '--email', required=False)
    plac.call(remove, 'value', type=int, required=True, '--dept', required=False, '--email', required=False)

@plac.annotations(
    filepath=('Loads the file to the database.', 'option', 'f', str),
)
def load(filepath):
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

@plac.annotations(
    output=('Shows information about user or dept.', 'option', 'o', str),
    dept=('Department to filter by.', 'option', 'd', str),
    email=('Email to filter by.', 'option', 'e', str),
)
def show(output=None, dept=None, email=None):
    """Shows information about user or dept."""
    result = core.read(dept=dept, email=email)
    if output:
        with open(output, "w") as output_file:
            output_file.write(json.dumps(result))

    if len(result) == 0:
        print("Nothing to show")

    table = Table(title="Dunder Mifflin Report")
    for key in result[0]:
        table.add_column(key.title().replace("_", " "), style="magenta")

    for person in result:
        person["value"] = f"{person['value']:.2f}"
        person["balance"] = f"{person['balance']:.2f}"
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)

@plac.annotations(
    value=('Add points to the user or dept.', 'argument', 'value', int),
    dept=('Department to filter by.', 'option', 'd', str),
    email=('Email to filter by.', 'option', 'e', str),
)
def add(value, dept=None, email=None):
    """Add points to the user or dept."""
    core.add(value, dept=dept, email=email)
    show(dept=dept, email=email)

@plac.annotations(
    value=('Removes points from the user or dept.', 'argument', 'value', int),
    dept=('Department to filter by.', 'option', 'd', str),
    email=('Email to filter by.', 'option', 'e', str),
)
def remove(value, dept=None, email=None):
    """Removes points from the user or dept."""
    core.add(-value, dept=dept, email=email)
    show(dept=dept, email=email)

if __name__ == '__main__':
    plac.call(main)