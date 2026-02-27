import typer

from venvs import converge, create, find, remove, temporary

app = typer.Typer(
    help="Centralized virtual environments.",
    add_completion=False,  # Equivalent to disabling auto-completion in click
    pretty_exceptions_enable=False,
)