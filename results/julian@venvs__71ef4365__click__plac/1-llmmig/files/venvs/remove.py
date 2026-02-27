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
def main(force: ("Ignore errors if the virtualenv does not exist.", "flag", "f") = False, *names):
    """
    Remove an ad hoc virtualenv.
    """
    exit_code = run(locator=None, filesystem=None, names=names, force=force) or 0
    return exit_code


if __name__ == "__main__":
    plac.call(main)
