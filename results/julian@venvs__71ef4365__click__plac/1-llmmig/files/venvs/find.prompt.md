The following Python code currently uses the library "click" version 8.1.7.
Migrate this code to use the library "plac" version 1.4.5 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "click" to "plac".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "click" and "plac".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""
CLI for finding the location of appropriate virtual environments.
"""

from functools import partial
import sys

from filesystems import Path
import click
import filesystems.click

from venvs.common import _FILESYSTEM, _ROOT


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


@click.group(
    context_settings=dict(help_option_names=["-h", "--help"]),
    invoke_without_command=True,
)
@_FILESYSTEM
@_ROOT
@click.option(
    "-E",
    "--existing-only",
    flag_value=True,
    help="Only consider existing virtualenvs.",
)
@click.pass_context
def main(context, locator, existing_only, filesystem):
    """
    Find a virtualenv in the store.
    """
    if context.invoked_subcommand is None:
        click.echo(locator.root)
    else:
        context.obj = dict(
            locate=partial(
                run,
                locator=locator,
                existing_only=existing_only,
                filesystem=filesystem,
            ),
        )


@main.command()
@click.argument("directory", required=False, type=filesystems.click.PATH)
@click.argument("binary", required=False)
@click.pass_context
def directory(context, directory, binary):
    """
    Find the virtualenv given the project's path.
    """
    locate = context.obj["locate"]
    context.exit(
        locate(directory=directory or Path.cwd(), binary=binary) or 0,
    )


@main.command()
@click.argument("name")
@click.argument("binary", required=False)
@click.pass_context
def name(context, name, binary):
    """
    Find the virtualenv given the project's name.
    """
    locate = context.obj["locate"]
    context.exit(locate(name=name, binary=binary) or 0)

```