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

_INSTALL = typer.Option(
    None,
    "-i",
    "--install",
    help=(
        "install the given specifier (package) into the "
        "virtualenv with pip after it is created"
    ),
    multiple=True,
)
_REQUIREMENTS = typer.Option(
    None,
    "-r",
    "--requirement",
    help=(
        "install the given requirements file into the "
        "virtualenv with pip after it is created"
    ),
    multiple=True,
)


@_FILESYSTEM
@_LINK_DIR
@_ROOT
@_INSTALL
@_REQUIREMENTS
def main(
    filesystem,
    link_dir,
    name: str = typer.Argument(None, required=False),
    locator=None,
    installs: list[str] = _INSTALL,
    links: list[str] = typer.Option(None, "-l", "--link", help=(
        "After installing any specified packages, link the specified "
        "binaries into the directory they would have been installed into "
        "globally."
    ), multiple=True),
    recreate: bool = typer.Option(False, "-R", "--recreate", help="recreate the virtualenv if it already exists"),
    virtualenv_args: list[str] = typer.Argument(..., nargs=-1),
    persist: bool = typer.Option(False, "--persist/--no-persist", "-p", help="Add to config file when installing."),
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
