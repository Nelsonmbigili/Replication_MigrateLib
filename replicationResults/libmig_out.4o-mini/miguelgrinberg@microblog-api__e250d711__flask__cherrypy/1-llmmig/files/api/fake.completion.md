### Explanation of Changes

To migrate the code from using the Flask framework to CherryPy, the following changes were made:

1. **Import Changes**: The `flask` and `click` imports were removed, as CherryPy does not use these libraries for command-line interface (CLI) commands.
2. **CLI Command Handling**: CherryPy does not have a built-in CLI command system like Flask's `@click.command()`. Instead, we will create a simple function that can be called directly to simulate the CLI behavior.
3. **Blueprint Removal**: The `Blueprint` concept from Flask is not present in CherryPy, so the `fake` blueprint was removed.
4. **Session Management**: The session management remains the same since it is part of the SQLAlchemy integration, which is still applicable.
5. **Function Calls**: The functions `users` and `posts` are now standalone functions that can be called directly.

Here is the modified code:

```python
import random
from faker import Faker
from api.app import db
from api.models import User, Post

faker = Faker()

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

# Example of how to call the functions
# create_users(10)
# create_posts(5)
```

### Note
In the modified code, the functions `create_users` and `create_posts` can be called directly with the desired number of users or posts to create. You would need to implement a separate mechanism to handle command-line arguments if you want to maintain CLI functionality similar to Flask's `click`.