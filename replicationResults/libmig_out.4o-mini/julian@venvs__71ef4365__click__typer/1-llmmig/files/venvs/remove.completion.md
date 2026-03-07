### Explanation of Changes
To migrate the code from using the `click` library to the `typer` library, the following changes were made:

1. **Import Statement**: The import statement for `click` was replaced with `typer`.
2. **Decorator Changes**: The `@click.option` and `@click.argument` decorators were replaced with `typer.Option` and `typer.Argument`, respectively.
3. **Context Handling**: The `click.pass_context` decorator was removed, as `typer` automatically handles context and does not require it.
4. **Function Signature**: The `main` function's signature was updated to directly accept parameters for options and arguments, as `typer` handles this differently than `click`.

### Modified Code
```python
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
```