"""
CLI for deleting virtual environments imperatively.
"""

from filesystems.exceptions import FileNotFound
import typer

from venvs.common import _EX_NOINPUT, _FILESYSTEM, _ROOT

app = typer.Typer()

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
@app.command()
def main(
    names: list[str] = typer.Argument(..., help="Names of the virtual environments to remove."),
    force: bool = typer.Option(False, "--force", "-f", help="Ignore errors if the virtualenv does not exist.")
):
    """
    Remove an ad hoc virtualenv.
    """
    exit_code = run(locator=None, filesystem=None, names=names, force=force) or 0
    raise typer.Exit(code=exit_code)


if __name__ == "__main__":
    app()
