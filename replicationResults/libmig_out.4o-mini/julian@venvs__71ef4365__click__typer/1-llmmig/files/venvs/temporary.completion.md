### Explanation of Changes
To migrate the code from using the `click` library to the `typer` library, the following changes were made:

1. **Import Statement**: The import statement for `click` was replaced with `typer`.
2. **Function Signature**: The `@click.command()` decorator was removed, as `typer` automatically creates a command-line interface from the function signature.
3. **Output Function**: The `click.echo()` function was replaced with `typer.echo()`, which serves the same purpose in `typer`.
4. **Parameter Handling**: The parameters for the main function remain unchanged, as `typer` handles them similarly to `click`.

Here is the modified code:

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