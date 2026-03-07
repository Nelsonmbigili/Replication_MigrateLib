"""
CLI for deleting virtual environments imperatively.
"""

from filesystems.exceptions import FileNotFound
import typer

from venvs.common import _EX_NOINPUT, _FILESYSTEM, _ROOT


def run(locator, filesystem, names, force):
    """
    Remove an ad hoc virtual environment.
    """
    for name in names:
        virtualenv = locator.for_name(name=name)
        try:
            virtualenv.remove_from(filesystem=filesystem)
        except FileNotFound:
            if not force:
                return _EX_NOINPUT


@_FILESYSTEM
@_ROOT
def main(
    names: list[str] = typer.Argument(...),
    force: bool = typer.Option(False, "--force", "-f", help="Ignore errors if the virtualenv does not exist."),
):
    """
    Remove an ad hoc virtualenv.
    """
    raise typer.Exit(run(locator, filesystem, names, force) or 0)
