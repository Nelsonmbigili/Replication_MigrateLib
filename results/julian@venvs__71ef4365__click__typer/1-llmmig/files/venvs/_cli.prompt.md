The following Python code currently uses the library "click" version 8.1.7.
Migrate this code to use the library "typer" version 0.15.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "click" to "typer".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "click" and "typer".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import click

from venvs import converge, create, find, remove, temporary


@click.group(context_settings=dict(help_option_names=["--help", "-h"]))
@click.version_option(prog_name="venvs")
def main():
    """
    Centralized virtual environments.
    """


main.command(name="converge")(converge.main)
main.command(name="create")(create.main)
main.add_command(find.main, name="find")
main.command(name="remove")(remove.main)
main.command(name="temporary")(temporary.main)

```