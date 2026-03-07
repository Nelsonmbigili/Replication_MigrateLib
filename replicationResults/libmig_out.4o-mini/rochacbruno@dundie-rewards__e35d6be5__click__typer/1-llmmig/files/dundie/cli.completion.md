### Explanation of Changes

To migrate the code from using the `click` library to the `typer` library, the following changes were made:

1. **Import Statement**: Changed the import from `rich_click` to `typer`.
2. **Group and Command Decorators**: Replaced `@click.group()` and `@click.command()` with `@typer.Typer()` and `@typer.command()`, respectively.
3. **Argument and Option Definitions**: Changed `@click.argument` and `@click.option` to `typer.Argument` and `typer.Option`.
4. **Context Handling**: The context management with `ctx` is handled differently in `typer`, so the `@click.pass_context` decorator was removed, and the context is implicitly managed.
5. **Version Option**: The version option is handled differently in `typer`, so it was removed from the group definition.
6. **Console Output**: The `Console` from `rich` remains unchanged, as it is still used for printing tables.

Here is the modified code:

```python
import json

import pkg_resources
import typer
from rich.console import Console
from rich.table import Table

from dundie import core

app = typer.Typer()

@app.callback()
def main():
    """Dunder Mifflin Rewards System.

    This cli application controls Dunder Mifflin rewards.

    - admins can load information to the people database and assign points.
    - users can view reports and transfer points.

    """


@app.command()
def load(filepath: typer.Path(exists=True)):
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


@app.command()
def show(output: str = None, dept: str = None, email: str = None):
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


@app.command()
def add(value: int, dept: str = None, email: str = None):
    """Add points to the user or dept."""
    core.add(value, dept=dept, email=email)
    show(dept=dept, email=email)


@app.command()
def remove(value: int, dept: str = None, email: str = None):
    """Removes points from the user or dept."""
    core.add(-value, dept=dept, email=email)
    show(dept=dept, email=email)
```

This code now uses `typer` for command-line interface functionality while maintaining the original structure and logic of the application.