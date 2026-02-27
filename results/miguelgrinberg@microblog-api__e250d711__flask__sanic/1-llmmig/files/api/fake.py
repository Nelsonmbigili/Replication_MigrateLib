import random
import click
from sanic import Blueprint, Sanic
from faker import Faker
from api.app import db
from api.models import User, Post

app = Sanic("FakeDataApp")  # Create a Sanic app instance
fake = Blueprint('fake')  # Replace Flask's Blueprint with Sanic's Blueprint
faker = Faker()


@fake.listener('before_server_start')
def setup(app, loop):
    """Optional: Add any setup logic here if needed."""
    pass


@app.cli.command()
@click.argument('num', type=int)
async def users(num):  # pragma: no cover
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


@app.cli.command()
@click.argument('num', type=int)
async def posts(num):  # pragma: no cover
    """Create the given number of fake posts, assigned to random users."""
    users = db.session.scalars(User.select()).all()
    for i in range(num):
        user = random.choice(users)
        post = Post(text=faker.paragraph(), author=user,
                    timestamp=faker.date_time_this_year())
        db.session.add(post)
    db.session.commit()
    print(num, 'posts added.')


# Register the blueprint with the Sanic app
app.blueprint(fake)
