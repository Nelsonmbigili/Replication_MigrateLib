import json

import pkg_resources
import typer
from rich.console import Console
from rich.table import Table

from dundie import core

app = typer.Typer(help="""Dunder Mifflin Rewards System.

This CLI application controls Dunder Mifflin rewards.

- Admins can load information to the people database and assign points.
- Users can view reports and transfer points.
""")

@app.command()
def version():
    """Show the version of the application."""
    typer.echo(pkg_resources.get_distribution("dundie").version)


@app.command()
def load(
    filepath: str = typer.Argument(..., help="Path to the file to load", exists=True)
):
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
def show(
    dept: str = typer.Option(None, help="Filter by department"),
    email: str = typer.Option(None, help="Filter by email"),
    output: str = typer.Option(None, help="Output file to save the results"),
):
    """Shows information about user or dept."""
    query = {"dept": dept, "email": email}
    result = core.read(**query)
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
def add(
    ctx: typer.Context,
    value: int = typer.Argument(..., help="Value to add"),
    dept: str = typer.Option(None, help="Filter by department"),
    email: str = typer.Option(None, help="Filter by email"),
):
    """Add points to the user or dept."""
    query = {"dept": dept, "email": email}
    core.add(value, **query)
    ctx.invoke(show, **query)


@app.command()
def remove(
    ctx: typer.Context,
    value: int = typer.Argument(..., help="Value to remove"),
    dept: str = typer.Option(None, help="Filter by department"),
    email: str = typer.Option(None, help="Filter by email"),
):
    """Removes points from the user or dept."""
    query = {"dept": dept, "email": email}
    core.add(-value, **query)
    ctx.invoke(show, **query)


if __name__ == "__main__":
    app()
