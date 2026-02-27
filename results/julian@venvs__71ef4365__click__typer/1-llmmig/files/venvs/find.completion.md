### Explanation of Changes

To migrate the code from `click` to `typer`, the following changes were made:

1. **Import Replacement**: Replaced `click` imports with `typer`.
2. **Command Group**: Replaced `@click.group` with `typer.Typer()` to define the CLI application.
3. **Command Registration**: Replaced `@main.command()` with function decorators directly registered to the `typer.Typer` instance.
4. **Options and Arguments**: Replaced `@click.option` and `@click.argument` with `typer.Option` and `typer.Argument` respectively.
5. **Context Handling**: Replaced `@click.pass_context` and `context.obj` with `typer.Context` and `context.obj` (typer supports a similar mechanism for passing objects).
6. **Help Options**: Typer automatically handles help options (`-h` and `--help`), so no need to specify `help_option_names`.
7. **Filesystem Integration**: Adjusted the `_FILESYSTEM` and `_ROOT` decorators to work with Typer's structure.

### Modified Code

```python
"""
CLI for finding the location of appropriate virtual environments.
"""

from functools import partial
import sys

from filesystems import Path
import typer
import filesystems.click

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


@_FILESYSTEM
@_ROOT
@app.callback(invoke_without_command=True)
def main(
    context: typer.Context,
    existing_only: bool = typer.Option(
        False, "-E", "--existing-only", help="Only consider existing virtualenvs."
    ),
):
    """
    Find a virtualenv in the store.
    """
    locator = context.meta["locator"]
    filesystem = context.meta["filesystem"]

    if context.invoked_subcommand is None:
        typer.echo(locator.root)
    else:
        context.obj = dict(
            locate=partial(
                run,
                locator=locator,
                existing_only=existing_only,
                filesystem=filesystem,
            ),
        )


@app.command()
def directory(
    context: typer.Context,
    directory: Path = typer.Argument(None, help="The project's path."),
    binary: str = typer.Argument(None, help="The binary to locate."),
):
    """
    Find the virtualenv given the project's path.
    """
    locate = context.obj["locate"]
    context.exit(
        locate(directory=directory or Path.cwd(), binary=binary) or 0,
    )


@app.command()
def name(
    context: typer.Context,
    name: str = typer.Argument(..., help="The project's name."),
    binary: str = typer.Argument(None, help="The binary to locate."),
):
    """
    Find the virtualenv given the project's name.
    """
    locate = context.obj["locate"]
    context.exit(locate(name=name, binary=binary) or 0)


if __name__ == "__main__":
    app()
```

### Key Notes:
- The `typer.Typer` instance (`app`) replaces the `@click.group` decorator.
- The `@app.callback` decorator is used for the main command, replacing `@click.group`.
- `typer.Option` and `typer.Argument` replace `@click.option` and `@click.argument`.
- The `context.meta` dictionary is used to pass `_FILESYSTEM` and `_ROOT` values into the `main` function.
- The `context.obj` mechanism remains similar to `click` for passing objects between commands.