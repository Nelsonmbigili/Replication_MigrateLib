### Explanation of Changes

To migrate the code from using the `click` library to the `typer` library, the following changes were made:

1. **Import Statements**: The import of `click` was replaced with `typer`. The `filesystems.click` import was removed since `typer` does not have a direct equivalent for that.
  
2. **Command Group and Options**: The `@click.group` decorator was replaced with `@typer.Typer()`, and the options were defined using `typer.Option` instead of `click.option`.

3. **Context Management**: The context management with `@click.pass_context` was replaced with `typer.Context` and the use of `typer.Option` to handle options directly in the function parameters.

4. **Command Functions**: The command functions were updated to use `typer.Argument` instead of `click.argument`, and the way to access the context object was simplified since `typer` handles this differently.

5. **Output**: The `click.echo` function was used to print output, which is replaced with `typer.echo`.

6. **Exit Codes**: The `context.exit` method was replaced with `typer.Exit` to handle exit codes.

Here is the modified code:

```python
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
```

This code now uses `typer` for command-line interface functionality while maintaining the original structure and logic of the application.