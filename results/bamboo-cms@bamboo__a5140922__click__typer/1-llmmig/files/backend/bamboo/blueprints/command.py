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
