import plac
from flask import Blueprint

from bamboo.database import db

command = Blueprint("command", __name__, cli_group=None)


def create_tables() -> None:
    """Create all tables."""
    db.create_all()
    print("Tables created.")


def drop_tables() -> None:
    """Drop all tables."""
    db.drop_all()
    print("Tables dropped.")


def create_admin(
    username: str, 
    password: str, 
    fullname: str, 
    email: str
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
    print(f"Admin user {username} has been created.")


def main():
    plac.Interpreter.call(create_tables)
    plac.Interpreter.call(drop_tables)
    plac.Interpreter.call(create_admin)


if __name__ == "__main__":
    plac.call(main)
