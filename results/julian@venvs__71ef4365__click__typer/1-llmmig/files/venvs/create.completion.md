### Explanation of Changes
To migrate the code from `click` to `typer`, the following changes were made:
1. Replaced `click.option` with `typer.Option` for defining command-line options.
2. Replaced `click.argument` with `typer.Argument` for defining command-line arguments.
3. Removed the use of decorators for options and arguments, as `typer` uses function parameters with type annotations to define them.
4. Replaced `click.BadParameter` with `typer.BadParameter` for error handling.
5. Updated the function signature to include the options and arguments directly as parameters, as `typer` uses function parameters to define the CLI interface.
6. Updated the `main` function to be decorated with `@app.command()` to register it as a command in `typer`.

Below is the modified code:

### Modified Code
```python
"""
venvs creates virtualenvs.

By default it places them in the appropriate data directory for your platform
(See `platformdirs <https://pypi.python.org/pypi/platformdirs>`_), but it will
also respect the :envvar:`WORKON_HOME` environment variable for compatibility
with :command:`mkvirtualenv`.
"""

from functools import partial

from filesystems import Path
from packaging.requirements import Requirement
import typer

from venvs import _config
from venvs.common import _FILESYSTEM, _LINK_DIR, _ROOT

app = typer.Typer()

@app.command()
def main(
    filesystem: str = typer.Option(..., help="Filesystem to use."),
    link_dir: str = typer.Option(..., help="Directory for linking."),
    name: str = typer.Argument(None, help="Name of the virtualenv."),
    locator: str = typer.Option(..., help="Locator for the virtualenv."),
    installs: list[str] = typer.Option(
        [], "-i", "--install", help="Install the given specifier (package) into the virtualenv with pip after it is created."
    ),
    links: list[str] = typer.Option(
        [], "-l", "--link", help="After installing any specified packages, link the specified binaries into the directory they would have been installed into globally."
    ),
    requirements: list[str] = typer.Option(
        [], "-r", "--requirement", help="Install the given requirements file into the virtualenv with pip after it is created."
    ),
    recreate: bool = typer.Option(
        False, "-R", "--recreate", help="Recreate the virtualenv if it already exists."
    ),
    virtualenv_args: list[str] = typer.Argument(
        [], help="Additional arguments for the virtualenv.", show_default=False
    ),
    persist: bool = typer.Option(
        False, "--persist/--no-persist", "-p", help="Add to config file when installing."
    ),
):
    """
    Create a new ad hoc virtualenv.
    """
    if name:
        virtualenv = locator.for_name(name=name)
    elif len(installs) == 1:
        # When there's just one package to install, default to using that name.
        (requirement,) = installs
        name = Requirement(requirement).name
        virtualenv = locator.for_name(name=name)
    elif installs:
        raise typer.BadParameter("A name is required.")
    elif len(links) == 1:
        # When there's just one binary to link, go for the gold.
        (name,) = installs = links
        virtualenv = locator.for_name(name=name)
    else:
        virtualenv = locator.for_directory(directory=Path.cwd())

    if recreate:
        act = partial(virtualenv.recreate_on, filesystem=filesystem)
    else:
        act = virtualenv.create

    act(arguments=virtualenv_args)
    virtualenv.install(packages=installs, requirements=requirements)

    for link in links:
        filesystem.link(
            source=virtualenv.binary(name=link),
            to=link_dir.descendant(link),
        )

    if persist:
        _config.add_virtualenv(
            filesystem=filesystem,
            locator=locator,
            installs=installs,
            links=links,
            name=name,
        )

if __name__ == "__main__":
    app()
```

### Key Points
- The `typer.Option` and `typer.Argument` are used to define options and arguments, respectively, directly in the function signature.
- The `@app.command()` decorator is used to register the `main` function as a command in the `typer` application.
- The `typer.BadParameter` exception is used for parameter validation errors.
- The `typer` library simplifies the CLI definition by using type annotations and function parameters, reducing the need for decorators for each option or argument.