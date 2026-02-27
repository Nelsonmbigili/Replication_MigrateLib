"""
CLI for finding the location of appropriate virtual environments.
"""

from functools import partial
import sys

from filesystems import Path
import plac
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


def main(
    existing_only: ("Only consider existing virtualenvs.", "flag", "E") = False,
    directory: ("Find the virtualenv given the project's path.", "option", None) = None,
    binary: ("Optional binary to locate within the virtualenv.", "option", None) = None,
    name: ("Find the virtualenv given the project's name.", "option", None) = None,
):
    """
    Find a virtualenv in the store.
    """
    # Initialize locator and filesystem using decorators
    locator = _ROOT()
    filesystem = _FILESYSTEM()

    if directory:
        # Handle the "directory" subcommand
        result = run(
            locator=locator,
            filesystem=filesystem,
            directory=Path(directory),
            binary=binary,
            existing_only=existing_only,
        )
        sys.exit(result or 0)
    elif name:
        # Handle the "name" subcommand
        result = run(
            locator=locator,
            filesystem=filesystem,
            name=name,
            binary=binary,
            existing_only=existing_only,
        )
        sys.exit(result or 0)
    else:
        # Default behavior: print the root of the locator
        sys.stdout.write(str(locator.root))
        sys.stdout.write("\n")


if __name__ == "__main__":
    plac.call(main)
