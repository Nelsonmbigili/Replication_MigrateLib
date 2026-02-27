"""
venvs creates virtualenvs.

By default it places them in the appropriate data directory for your platform
(See `platformdirs <https://pypi.python.org/pypi/platformdirs>`_), but it will
also respect the :envvar:`WORKON_HOME` environment variable for compatibility
with :command:`mkvirtualenv`.

Arguments:
    name: The name of the virtualenv to create (optional).
    virtualenv_args: Additional arguments to pass to the virtualenv creation process.

Options:
    --install (-i): Install the given specifier (package) into the virtualenv with pip after it is created.
    --requirement (-r): Install the given requirements file into the virtualenv with pip after it is created.
    --link (-l): After installing any specified packages, link the specified binaries into the directory they would have been installed into globally.
    --recreate (-R): Recreate the virtualenv if it already exists.
    --persist (-p): Add to config file when installing (default: False).
"""

from functools import partial

from filesystems import Path
from packaging.requirements import Requirement
import plac

from venvs import _config
from venvs.common import _FILESYSTEM, _LINK_DIR, _ROOT

_INSTALL = click.option(
    "-i",
    "--install",
    "installs",
    multiple=True,
    help=(
        "install the given specifier (package) into the "
        "virtualenv with pip after it is created"
    ),
)
_REQUIREMENTS = click.option(
    "-r",
    "--requirement",
    "requirements",
    multiple=True,
    help=(
        "install the given requirements file into the "
        "virtualenv with pip after it is created"
    ),
)


@_FILESYSTEM
@_LINK_DIR
@_ROOT
@_INSTALL
@_REQUIREMENTS
@click.option(
    "-l",
    "--link",
    "links",
    multiple=True,
    help=(
        "After installing any specified packages, link the specified "
        "binaries into the directory they would have been installed into "
        "globally."
    ),
)
@click.option(
    "-R",
    "--recreate",
    flag_value=True,
    help="recreate the virtualenv if it already exists",
)
@click.option(
    "--persist/--no-persist",
    "-p",
    is_flag=True,
    default=False,
    help="Add to config file when installing.",
)
@click.argument("name", required=False)
@click.argument("virtualenv_args", nargs=-1, type=click.UNPROCESSED)
def main(
    filesystem,
    link_dir,
    name: ("The name of the virtualenv to create", "positional", None, str) = None,
    *virtualenv_args: ("Additional arguments for virtualenv creation",),
    installs: ("Install the given specifier (package)", "option", "i", str) = (),
    requirements: ("Install the given requirements file", "option", "r", str) = (),
    links: ("Link the specified binaries", "option", "l", str) = (),
    recreate: ("Recreate the virtualenv if it exists", "flag", "R") = False,
    persist: ("Add to config file when installing", "flag", "p") = False,
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
        raise ValueError("A name is required.")
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
    plac.call(main)