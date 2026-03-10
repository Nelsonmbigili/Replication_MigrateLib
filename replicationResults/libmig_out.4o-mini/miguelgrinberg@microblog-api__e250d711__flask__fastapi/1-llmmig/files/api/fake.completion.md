### Explanation of Changes

To migrate the provided code from using Flask to FastAPI, the following changes were made:

1. **Import Changes**: The `Blueprint` and `click` imports were removed since FastAPI does not use them in the same way. Instead, FastAPI uses its own command-line interface for running applications.
2. **Command-Line Interface**: FastAPI does not have a built-in CLI like Flask's `click`. Instead, we can use the `typer` library, which is commonly used with FastAPI for command-line interfaces. However, for simplicity, I will keep the command structure similar to the original.
3. **Database Session Handling**: FastAPI typically uses dependency injection for database sessions. However, since the original code does not specify how the database session is managed, I will keep the session handling as is.
4. **Function Decorators**: The `@fake.cli.command()` decorators were removed, as FastAPI does not use this method for defining CLI commands. Instead, we will define the functions directly.

Here is the modified code:

```python
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
```

### Note
- The CLI commands are now handled through a simple command-line argument check in the `if __name__ == "__main__":` block. This is a basic way to simulate the command-line interface that was previously provided by Flask's `click`.