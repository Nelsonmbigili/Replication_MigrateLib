"""
CLI for deleting virtual environments imperatively.
"""

from filesystems.exceptions import FileNotFound
import plac

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
@plac.annotations(
    force=("Ignore errors if the virtualenv does not exist.", "flag", "f"),
    names=("Names of the virtual environments to remove.", "positional", None)
)
def main(force=False, names=()):
    """
    Remove an ad hoc virtualenv.
    """
    return run(locator, filesystem, names, force) or 0

if __name__ == "__main__":
    plac.call(main)
