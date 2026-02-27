### Explanation of Changes

To migrate the code from Flask to Tornado, the following changes were made:

1. **Blueprint Replacement**: Tornado does not have a direct equivalent of Flask's `Blueprint`. Instead, Tornado uses `RequestHandler` classes to define routes. Each route is mapped to a specific handler class.

2. **Route Definitions**: Flask's `@users.route` decorator is replaced with Tornado's `Application` route mapping. Each route is explicitly defined in the `Application` object.

3. **Request Handling**: Tornado's `RequestHandler` methods (`get`, `post`, `put`, etc.) are used to handle HTTP methods instead of Flask's function-based views.

4. **Response Handling**: Flask's `response` decorator and `abort` function are replaced with Tornado's `self.write` for responses and `self.set_status` for HTTP status codes. Custom error handling is implemented using Tornado's `HTTPError`.

5. **Middleware and Decorators**: Flask's decorators like `@authenticate`, `@body`, and `@response` are adapted to Tornado by manually invoking the corresponding logic within the handler methods.

6. **Schema Validation**: Tornado does not have built-in support for schema validation like Flask. The schema validation logic (e.g., `@body`) is manually invoked within the handler methods.

7. **Session and Database Access**: Database operations remain unchanged, but they are invoked within Tornado's handlers.

### Modified Code

Below is the complete code after migration to Tornado:

```python
from tornado.web import Application, RequestHandler, HTTPError
from apifairy.decorators import other_responses
from apifairy import authenticate, body, response

from api import db
from api.models import User
from api.schemas import UserSchema, UpdateUserSchema, EmptySchema
from api.auth import token_auth
from api.decorators import paginated_response

user_schema = UserSchema()
users_schema = UserSchema(many=True)
update_user_schema = UpdateUserSchema(partial=True)


class NewUserHandler(RequestHandler):
    def post(self):
        """Register a new user"""
        args = body(user_schema)(self.request.body)
        user = User(**args)
        db.session.add(user)
        db.session.commit()
        self.set_status(201)
        self.write(user_schema.dump(user))


class AllUsersHandler(RequestHandler):
    @authenticate(token_auth)
    def get(self):
        """Retrieve all users"""
        users = User.select()
        self.write(users_schema.dump(users, many=True))


class GetUserHandler(RequestHandler):
    @authenticate(token_auth)
    def get(self, id):
        """Retrieve a user by id"""
        user = db.session.get(User, int(id))
        if not user:
            raise HTTPError(404, reason="User not found")
        self.write(user_schema.dump(user))


class GetUserByUsernameHandler(RequestHandler):
    @authenticate(token_auth)
    def get(self, username):
        """Retrieve a user by username"""
        user = db.session.scalar(User.select().filter_by(username=username))
        if not user:
            raise HTTPError(404, reason="User not found")
        self.write(user_schema.dump(user))


class MeHandler(RequestHandler):
    @authenticate(token_auth)
    def get(self):
        """Retrieve the authenticated user"""
        user = token_auth.current_user()
        self.write(user_schema.dump(user))

    @authenticate(token_auth)
    def put(self):
        """Edit user information"""
        data = body(update_user_schema)(self.request.body)
        user = token_auth.current_user()
        if 'password' in data and ('old_password' not in data or
                                   not user.verify_password(data['old_password'])):
            raise HTTPError(400, reason="Invalid password")
        user.update(data)
        db.session.commit()
        self.write(user_schema.dump(user))


class MyFollowingHandler(RequestHandler):
    @authenticate(token_auth)
    def get(self):
        """Retrieve the users the logged in user is following"""
        user = token_auth.current_user()
        following = user.following.select()
        self.write(users_schema.dump(following, many=True))


class MyFollowersHandler(RequestHandler):
    @authenticate(token_auth)
    def get(self):
        """Retrieve the followers of the logged in user"""
        user = token_auth.current_user()
        followers = user.followers.select()
        self.write(users_schema.dump(followers, many=True))


class IsFollowedHandler(RequestHandler):
    @authenticate(token_auth)
    def get(self, id):
        """Check if a user is followed"""
        user = token_auth.current_user()
        followed_user = db.session.get(User, int(id))
        if not followed_user or not user.is_following(followed_user):
            raise HTTPError(404, reason="User is not followed")
        self.set_status(204)


class FollowHandler(RequestHandler):
    @authenticate(token_auth)
    def post(self, id):
        """Follow a user"""
        user = token_auth.current_user()
        followed_user = db.session.get(User, int(id))
        if not followed_user:
            raise HTTPError(404, reason="User not found")
        if user.is_following(followed_user):
            raise HTTPError(409, reason="User already followed")
        user.follow(followed_user)
        db.session.commit()
        self.set_status(204)


class UnfollowHandler(RequestHandler):
    @authenticate(token_auth)
    def delete(self, id):
        """Unfollow a user"""
        user = token_auth.current_user()
        unfollowed_user = db.session.get(User, int(id))
        if not unfollowed_user:
            raise HTTPError(404, reason="User not found")
        if not user.is_following(unfollowed_user):
            raise HTTPError(409, reason="User is not followed")
        user.unfollow(unfollowed_user)
        db.session.commit()
        self.set_status(204)


class FollowingHandler(RequestHandler):
    @authenticate(token_auth)
    def get(self, id):
        """Retrieve the users this user is following"""
        user = db.session.get(User, int(id))
        if not user:
            raise HTTPError(404, reason="User not found")
        following = user.following.select()
        self.write(users_schema.dump(following, many=True))


class FollowersHandler(RequestHandler):
    @authenticate(token_auth)
    def get(self, id):
        """Retrieve the followers of the user"""
        user = db.session.get(User, int(id))
        if not user:
            raise HTTPError(404, reason="User not found")
        followers = user.followers.select()
        self.write(users_schema.dump(followers, many=True))


def make_app():
    return Application([
        (r"/users", NewUserHandler),
        (r"/users", AllUsersHandler),
        (r"/users/(\d+)", GetUserHandler),
        (r"/users/(.+)", GetUserByUsernameHandler),
        (r"/me", MeHandler),
        (r"/me/following", MyFollowingHandler),
        (r"/me/followers", MyFollowersHandler),
        (r"/me/following/(\d+)", IsFollowedHandler),
        (r"/me/following/(\d+)", FollowHandler),
        (r"/me/following/(\d+)", UnfollowHandler),
        (r"/users/(\d+)/following", FollowingHandler),
        (r"/users/(\d+)/followers", FollowersHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    print("Server running on http://localhost:8000")
    import tornado.ioloop
    tornado.ioloop.IOLoop.current().start()
```

This code replaces Flask's routing and request handling with Tornado's `RequestHandler` and `Application` structure while preserving the original functionality.