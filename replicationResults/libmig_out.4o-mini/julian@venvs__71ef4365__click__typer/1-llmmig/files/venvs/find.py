"""
CLI for finding the location of appropriate virtual environments.
"""

from functools import partial
import sys

from filesystems import Path
import typer
from venvs.common import _FILESYSTEM, _ROOT

app = typer.Typer()

def run(
    locator,
    filesystem,
    binary=None,
    directory=None,
    name=None,
    existing_only=False,
):
    """
    Find the virtualenv associated with a given project given its name or path.

    If an optional binary is provided, the binary's path within the virtualenv
    is returned.
    """
    if directory is not None:
        virtualenv = locator.for_directory(directory=directory)
    else:
        if name is None:
            sys.stdout.write(str(locator.root))
            sys.stdout.write("\n")
            return

        virtualenv = locator.for_name(name=name)

    if existing_only and not virtualenv.exists_on(filesystem=filesystem):
        return 1

    if binary is not None:
        sys.stdout.write(str(virtualenv.binary(binary)))
    else:
        sys.stdout.write(str(virtualenv.path))

    sys.stdout.write("\n")


@app.callback()
def main(
    existing_only: bool = typer.Option(False, "-E", "--existing-only", help="Only consider existing virtualenvs."),
    locator=typer.Argument(...),
    filesystem=typer.Argument(...),
):
    """
    Find a virtualenv in the store.
    """
    if existing_only:
        locate = partial(run, locator=locator, existing_only=existing_only, filesystem=filesystem)
        typer.echo(locator.root)


@app.command()
def directory(
    directory: str = typer.Argument(None),
    binary: str = typer.Argument(None),
    locator=typer.Argument(...),
    existing_only: bool = typer.Option(False, "-E", "--existing-only", help="Only consider existing virtualenvs."),
):
    """
    Find the virtualenv given the project's path.
    """
    locate = partial(run, locator=locator, existing_only=existing_only)
    raise typer.Exit(code=locate(directory=directory or Path.cwd(), binary=binary) or 0)


@app.command()
def name(
    name: str = typer.Argument(...),
    binary: str = typer.Argument(None),
    locator=typer.Argument(...),
    existing_only: bool = typer.Option(False, "-E", "--existing-only", help="Only consider existing virtualenvs."),
):
    """
    Find the virtualenv given the project's name.
    """
    locate = partial(run, locator=locator, existing_only=existing_only)
    raise typer.Exit(code=locate(name=name, binary=binary) or 0)
