"""
CLI for managing a global temporary virtual environment.
"""

import plac

from venvs.common import _FILESYSTEM, _ROOT
from venvs.create import _INSTALL, _REQUIREMENTS


@_FILESYSTEM
@_ROOT
@_INSTALL
@_REQUIREMENTS
def main(filesystem, locator, installs, requirements):
    """
    Create or reuse the global temporary virtualenv.
    """
    temporary = locator.temporary()
    print(temporary.binary("python").dirname())
    temporary.recreate_on(filesystem=filesystem)
    temporary.install(packages=installs, requirements=requirements)


if __name__ == "__main__":
    plac.call(main)
