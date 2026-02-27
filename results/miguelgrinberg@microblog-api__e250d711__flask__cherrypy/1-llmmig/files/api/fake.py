import random
import cherrypy
from faker import Faker
from api.app import db
from api.models import User, Post

faker = Faker()

class FakeApp:
    @cherrypy.expose
    def users(self, num):  # pragma: no cover
        """Create the given number of fake users."""
        try:
            num = int(num)
        except ValueError:
            return "Invalid number of users. Please provide an integer."

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
        return f"{num} users added."

    @cherrypy.expose
    def posts(self, num):  # pragma: no cover
        """Create the given number of fake posts, assigned to random users."""
        try:
            num = int(num)
        except ValueError:
            return "Invalid number of posts. Please provide an integer."

        users = db.session.scalars(User.select()).all()
        for i in range(num):
            user = random.choice(users)
            post = Post(text=faker.paragraph(), author=user,
                        timestamp=faker.date_time_this_year())
            db.session.add(post)
        db.session.commit()
        return f"{num} posts added."


if __name__ == '__main__':
    cherrypy.quickstart(FakeApp())
