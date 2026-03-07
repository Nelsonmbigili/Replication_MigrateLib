"""
CLI for finding the location of appropriate virtual environments.
"""

from functools import partial
import sys

from filesystems import Path
import plac
import filesystems.plac

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


@plac.annotations(
    existing_only=("Only consider existing virtualenvs.", "flag", "E"),
    filesystem=_FILESYSTEM,
    locator=_ROOT,
)
def main(existing_only=False, filesystem=None, locator=None):
    """
    Find a virtualenv in the store.
    """
    if locator is None:
        print(locator.root)
    else:
        locate = partial(
            run,
            locator=locator,
            existing_only=existing_only,
            filesystem=filesystem,
        )
        return locate


@plac.annotations(
    directory=("The project's path.", "option", "d"),
    binary=("The binary to find.", "option", "b"),
)
def directory(directory=None, binary=None):
    """
    Find the virtualenv given the project's path.
    """
    locate = main()
    return locate(directory=directory or Path.cwd(), binary=binary) or 0


@plac.annotations(
    name=("The project's name.", "argument"),
    binary=("The binary to find.", "option", "b"),
)
def name(name, binary=None):
    """
    Find the virtualenv given the project's name.
    """
    locate = main()
    return locate(name=name, binary=binary) or 0


if __name__ == "__main__":
    plac.call(main)
