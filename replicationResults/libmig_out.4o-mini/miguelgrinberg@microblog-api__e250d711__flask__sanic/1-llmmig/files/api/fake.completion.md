### Explanation of Changes

To migrate the code from using the Flask framework to the Sanic framework, the following changes were made:

1. **Import Changes**: The `Blueprint` and `click` imports were replaced with Sanic's equivalent functionality. Sanic does not use `click` for command-line interface (CLI) commands, so the CLI commands were adapted to use Sanic's built-in command functionality.
  
2. **Blueprint Initialization**: The way to create a blueprint in Sanic is similar, but the import and usage context changes slightly.

3. **Database Session Handling**: Sanic does not have a built-in ORM like Flask-SQLAlchemy, so the database session handling may need to be adapted depending on the ORM being used. However, since the original code uses `db.session`, we assume that the same session management can be used with Sanic.

4. **CLI Command Registration**: The CLI commands are registered differently in Sanic. Instead of using `@fake.cli.command()`, we will use Sanic's command registration.

Here is the modified code:

```python
import random
from sanic import Blueprint, Sanic
from faker import Faker
from api.app import db
from api.models import User, Post

fake = Blueprint('fake', __name__)
faker = Faker()

app = Sanic(__name__)

@app.cli.command()
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
```

### Note
- The `async` keyword was added to the command functions to align with Sanic's asynchronous nature.
- The `app` instance of Sanic is created to register the CLI commands.