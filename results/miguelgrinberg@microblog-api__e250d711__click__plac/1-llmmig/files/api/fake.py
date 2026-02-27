import random
import plac
from flask import Blueprint
from faker import Faker
from api.app import db
from api.models import User, Post

fake = Blueprint('fake', __name__)
faker = Faker()


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


# Register commands with plac
@fake.route('/users/<int:num>', methods=['POST'])
def users_command(num):
    plac.call(users, [num])
    return f"{num} users added."


@fake.route('/posts/<int:num>', methods=['POST'])
def posts_command(num):
    plac.call(posts, [num])
    return f"{num} posts added."
