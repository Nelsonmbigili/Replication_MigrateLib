import random
from fastapi import FastAPI
from faker import Faker
from api.app import db
from api.models import User, Post

app = FastAPI()
faker = Faker()


@app.on_event("startup")
def startup_event():
    pass  # Placeholder for any startup actions if needed


def create_users(num):  # pragma: no cover
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


def create_posts(num):  # pragma: no cover
    """Create the given number of fake posts, assigned to random users."""
    users = db.session.scalars(User.select()).all()
    for i in range(num):
        user = random.choice(users)
        post = Post(text=faker.paragraph(), author=user,
                    timestamp=faker.date_time_this_year())
        db.session.add(post)
    db.session.commit()
    print(num, 'posts added.')


# Example usage (not part of the original code)
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "users" and len(sys.argv) == 3:
            create_users(int(sys.argv[2]))
        elif command == "posts" and len(sys.argv) == 3:
            create_posts(int(sys.argv[2]))
