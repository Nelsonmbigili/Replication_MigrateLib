### Explanation of Changes
To migrate the code from using the `click` library to the `typer` library, the following changes were made:
1. Replaced the `click.echo` function with the `typer.echo` function, as `typer` provides a similar utility for printing messages to the console.
2. Since the `main` function does not use any `click`-specific decorators or commands, no additional changes were required to adapt it to `typer`.

The rest of the code remains unchanged, as the migration only involves replacing `click`-specific functionality with its `typer` equivalent.

### Modified Code
```python
"""
CLI for managing a global temporary virtual environment.
"""

import typer

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
    typer.echo(temporary.binary("python").dirname())
    temporary.recreate_on(filesystem=filesystem)
    temporary.install(packages=installs, requirements=requirements)
```

This code now uses `typer.echo` instead of `click.echo`, completing the migration to the `typer` library.