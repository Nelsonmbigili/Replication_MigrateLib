import random
import typer
from fastapi import APIRouter
from faker import Faker
from api.app import db
from api.models import User, Post

fake_router = APIRouter()
faker = Faker()
app = typer.Typer()  # Typer app for CLI commands


@app.command()
def users(num: int):  # pragma: no cover
    """Create the given number of fake users."""
    users = []
    for i in range(num):
        user = User(username=faker.user_name(), email=faker.email(),
                    about_me=faker.sentence())
        db.session.add(user)
        users.append(user)

    # create some followers as well
    for user in users:
        num_followers = random.randint(0, 5)
        for i in range(num_followers):
            following = random.choice(users)
            if user != following:
                user.follow(following)

    db.session.commit()
    print(num, 'users added.')


@app.command()
def posts(num: int):  # pragma: no cover
    """Create the given number of fake posts, assigned to random users."""
    users = db.session.scalars(User.select()).all()
    for i in range(num):
        user = random.choice(users)
        post = Post(text=faker.paragraph(), author=user,
                    timestamp=faker.date_time_this_year())
        db.session.add(post)
    db.session.commit()
    print(num, 'posts added.')


# FastAPI router (if needed for API endpoints)
@fake_router.get("/")
def read_root():
    return {"message": "Fake data generator is ready!"}


# To run CLI commands, use Typer's app
if __name__ == "__main__":
    app()
