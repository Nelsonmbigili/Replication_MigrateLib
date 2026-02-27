import random
import argparse
from faker import Faker
from api.app import db
from api.models import User, Post

faker = Faker()

def create_fake_users(num):  # pragma: no cover
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

def create_fake_posts(num):  # pragma: no cover
    """Create the given number of fake posts, assigned to random users."""
    users = db.session.scalars(User.select()).all()
    for i in range(num):
        user = random.choice(users)
        post = Post(text=faker.paragraph(), author=user,
                    timestamp=faker.date_time_this_year())
        db.session.add(post)
    db.session.commit()
    print(num, 'posts added.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fake data generator for the application.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add 'users' command
    users_parser = subparsers.add_parser("users", help="Create fake users")
    users_parser.add_argument("num", type=int, help="Number of fake users to create")

    # Add 'posts' command
    posts_parser = subparsers.add_parser("posts", help="Create fake posts")
    posts_parser.add_argument("num", type=int, help="Number of fake posts to create")

    args = parser.parse_args()

    if args.command == "users":
        create_fake_users(args.num)
    elif args.command == "posts":
        create_fake_posts(args.num)
