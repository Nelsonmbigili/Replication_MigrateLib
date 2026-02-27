The following Python code currently uses the library "click" version 8.1.7.
Migrate this code to use the library "plac" version 1.4.5 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "click" to "plac".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "click" and "plac".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""
CLI for deleting virtual environments imperatively.
"""

from filesystems.exceptions import FileNotFound
import click

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
@click.option(
    "-f",
    "--force",
    flag_value=True,
    help="Ignore errors if the virtualenv does not exist.",
)
@click.argument("names", nargs=-1)
@click.pass_context
def main(context, **kwargs):
    """
    Remove an ad hoc virtualenv.
    """
    context.exit(run(**kwargs) or 0)

```