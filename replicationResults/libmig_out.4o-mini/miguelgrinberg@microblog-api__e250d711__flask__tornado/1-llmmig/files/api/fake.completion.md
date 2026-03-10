### Explanation of Changes

To migrate the provided code from using the Flask framework to the Tornado framework, the following changes were made:

1. **Import Changes**: The `flask` and `click` imports were removed, and the necessary Tornado imports were added.
2. **Blueprint Replacement**: Tornado does not have a direct equivalent to Flask's Blueprint. Instead, the command functions were defined as standalone functions.
3. **Database Session Handling**: The database session handling was adjusted to fit Tornado's asynchronous nature. However, since the original code does not use asynchronous features, the session handling remains synchronous.
4. **Command Line Interface**: Tornado does not have a built-in CLI like Flask's `click`. Therefore, the command functions were modified to be standalone functions that can be called directly instead of being registered as CLI commands.

Here is the modified code:

```python
import random
from tornado import ioloop
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

if __name__ == "__main__":
    # Example usage
    create_users(10)  # Replace with desired number of users
    create_posts(5)   # Replace with desired number of posts
    ioloop.IOLoop.current().start()
```

### Note
- The CLI functionality is not directly replicated in Tornado, so the functions `create_users` and `create_posts` can be called directly in the `if __name__ == "__main__":` block for demonstration purposes. In a real application, you might want to implement a different way to trigger these functions, such as through HTTP requests or a different command-line interface.