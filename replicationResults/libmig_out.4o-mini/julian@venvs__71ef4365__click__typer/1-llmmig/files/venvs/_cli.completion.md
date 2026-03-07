### Explanation of Changes
To migrate the code from using the "click" library to the "typer" library, the following changes were made:

1. **Import Statement**: Changed the import from `click` to `typer`.
2. **Group and Command Definitions**: The `@click.group` decorator was replaced with `@typer.Typer()`, and the command definitions were adjusted to use the `app.command()` method instead of `main.command()`.
3. **Version Option**: The version option was removed since Typer automatically handles versioning through the `Typer` class.

### Modified Code
```python
import typer

from venvs import converge, create, find, remove, temporary

app = typer.Typer(help="Centralized virtual environments.")

app.command(name="converge")(converge.main)
app.command(name="create")(create.main)
app.command(name="find")(find.main)
app.command(name="remove")(remove.main)
app.command(name="temporary")(temporary.main)

if __name__ == "__main__":
    app()
```