### Explanation of Changes:
To migrate the code from Flask to Sanic:
1. **Blueprint Replacement**: Flask's `Blueprint` is replaced with Sanic's `Blueprint`.
2. **CLI Commands**: Flask's CLI commands (`@fake.cli.command()`) are replaced with Sanic's CLI commands using `@app.cli.command`.
3. **Database Session Handling**: The database session handling remains the same since it is not tied to Flask or Sanic directly.
4. **Sanic App Initialization**: Sanic requires an app instance to register blueprints and CLI commands. A `Sanic` app instance is created and the blueprint is registered to it.
5. **Sanic-Specific Imports**: The necessary imports for Sanic are added.

### Modified Code:
```python
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
```

### Key Notes:
- The `@fake.cli.command()` decorator in Flask is replaced with `@app.cli.command()` in Sanic.
- The `Sanic` app instance (`app`) is created and the blueprint (`fake`) is registered to it using `app.blueprint(fake)`.
- The database session handling (`db.session.add`, `db.session.commit`) remains unchanged as it is not specific to Flask or Sanic.
- The `@fake.listener('before_server_start')` is added as a placeholder for any setup logic that might be needed before the server starts. This is optional and can be removed if not required.