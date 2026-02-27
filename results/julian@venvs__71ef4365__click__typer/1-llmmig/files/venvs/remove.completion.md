### Explanation of Changes
To migrate the code from `click` to `typer`, the following changes were made:
1. Replaced `click` imports and decorators with `typer` equivalents.
2. Used `typer.Option` for the `--force` option and `typer.Argument` for the `names` argument.
3. Removed the `@click.pass_context` decorator and replaced `context.exit()` with a direct return of the exit code, as `typer` does not use a `context` object in the same way.
4. Adjusted the function signature of `main` to directly accept parameters instead of using `**kwargs`, as `typer` automatically maps CLI arguments to function parameters.

### Modified Code
```python
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
```

### Key Notes
- The `typer.Typer` instance (`app`) is used to define the CLI application.
- The `main` function now directly accepts `names` and `force` as parameters, with `typer.Argument` and `typer.Option` used to define their CLI behavior.
- The `typer.Exit` exception is used to exit the program with the appropriate exit code, replacing `context.exit()` from `click`.
- The `if __name__ == "__main__":` block ensures the CLI application runs when the script is executed directly.