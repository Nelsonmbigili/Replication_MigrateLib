### Explanation of Changes:
To migrate from `click` to `typer`, the following changes were made:
1. Replaced `click` imports and functionality with `typer` equivalents:
   - `click.echo` was replaced with `typer.echo`.
   - `click.option` was replaced with `typer.Option`.
2. The `@command.cli.command` decorator was replaced with `@app.command` since `typer` uses an `App` object to define commands.
3. A `typer.Typer` instance (`app`) was created to replace the `Blueprint` object for CLI commands.
4. The `prompt` and `confirmation_prompt` options in `click.option` were replaced with `typer.Option` parameters using `prompt=True` and `confirmation_prompt=True`.

### Modified Code:
```python
import typer
from flask import Blueprint

from bamboo.database import db

app = typer.Typer()
command = Blueprint("command", __name__, cli_group=None)


@app.command(name="create-tables")
def create_tables() -> None:
    """Create all tables."""
    db.create_all()
    typer.echo("Tables created.")


@app.command(name="drop-tables")
def drop_tables() -> None:
    """Drop all tables."""
    db.drop_all()
    typer.echo("Tables dropped.")


@app.command(name="create-admin")
def create_admin(
    username: str = typer.Option(..., prompt=True, help="Admin username."),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, confirmation_prompt=True, help="Admin password."
    ),
    fullname: str = typer.Option(..., prompt=True, help="Admin full name."),
    email: str = typer.Option(..., prompt=True, help="Admin email."),
) -> None:
    """Create admin user."""
    from bamboo.database import models

    if (
        profile := db.session.scalars(db.select(models.Media).filter_by(path="user.png")).first()
    ) is None:
        profile = models.Media.from_file("user.png")
        db.session.add(profile)

    user = models.User(
        name=fullname,
        profile_image=profile,
        is_superuser=True,
        active=True,
        username=username,
        email=email,
    )
    user.password = password
    db.session.add(user)
    db.session.commit()
    typer.echo(f"Admin user {username} has been created.")
```

### Key Notes:
- The `typer.Typer` instance (`app`) is now the main entry point for CLI commands.
- The `Blueprint` object (`command`) remains unchanged because it is part of the Flask application and unrelated to the CLI migration.
- The `typer.Option` syntax is used to handle options and prompts, maintaining the same behavior as the original `click.option`.