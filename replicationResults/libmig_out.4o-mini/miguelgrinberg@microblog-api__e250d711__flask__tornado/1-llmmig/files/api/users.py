from apifairy.decorators import other_responses
import tornado.web
from apifairy import authenticate, body, response

from api import db
from api.models import User
from api.schemas import UserSchema, UpdateUserSchema, EmptySchema
from api.auth import token_auth
from api.decorators import paginated_response

user_schema = UserSchema()
users_schema = UserSchema(many=True)
update_user_schema = UpdateUserSchema(partial=True)

class UsersHandler(tornado.web.RequestHandler):

    @tornado.web.authenticated
    @body(user_schema)
    @response(user_schema, 201)
    def post(self):
        """Register a new user"""
        args = self.request.body
        user = User(**args)
        db.session.add(user)
        db.session.commit()
        self.set_status(201)
        self.write(user)

    @authenticate(token_auth)
    @paginated_response(users_schema)
    def get(self):
        """Retrieve all users"""
        self.write(User.select())

class UserDetailHandler(tornado.web.RequestHandler):

    @authenticate(token_auth)
    @response(user_schema)
    @other_responses({404: 'User not found'})
    def get(self, id):
        """Retrieve a user by id"""
        user = db.session.get(User, id)
        if not user:
            raise tornado.web.HTTPError(404)
        self.write(user)

    @authenticate(token_auth)
    @response(user_schema)
    @other_responses({404: 'User not found'})
    def get_by_username(self, username):
        """Retrieve a user by username"""
        user = db.session.scalar(User.select().filter_by(username=username))
        if not user:
            raise tornado.web.HTTPError(404)
        self.write(user)

    @authenticate(token_auth)
    @response(user_schema)
    def me(self):
        """Retrieve the authenticated user"""
        self.write(token_auth.current_user())

    @authenticate(token_auth)
    @body(update_user_schema)
    @response(user_schema)
    def put(self):
        """Edit user information"""
        data = self.request.body
        user = token_auth.current_user()
        if 'password' in data and ('old_password' not in data or
                                   not user.verify_password(data['old_password'])):
            raise tornado.web.HTTPError(400)
        user.update(data)
        db.session.commit()
        self.write(user)

    @authenticate(token_auth)
    @paginated_response(users_schema, order_by=User.username)
    def my_following(self):
        """Retrieve the users the logged in user is following"""
        user = token_auth.current_user()
        self.write(user.following.select())

    @authenticate(token_auth)
    @paginated_response(users_schema, order_by=User.username)
    def my_followers(self):
        """Retrieve the followers of the logged in user"""
        user = token_auth.current_user()
        self.write(user.followers.select())

    @authenticate(token_auth)
    @response(EmptySchema, status_code=204,
              description='User is followed.')
    @other_responses({404: 'User is not followed'})
    def is_followed(self, id):
        """Check if a user is followed"""
        user = token_auth.current_user()
        followed_user = db.session.get(User, id)
        if not followed_user:
            raise tornado.web.HTTPError(404)
        if not user.is_following(followed_user):
            raise tornado.web.HTTPError(404)
        self.set_status(204)

    @authenticate(token_auth)
    @response(EmptySchema, status_code=204,
              description='User followed successfully.')
    @other_responses({404: 'User not found', 409: 'User already followed.'})
    def follow(self, id):
        """Follow a user"""
        user = token_auth.current_user()
        followed_user = db.session.get(User, id)
        if not followed_user:
            raise tornado.web.HTTPError(404)
        if user.is_following(followed_user):
            raise tornado.web.HTTPError(409)
        user.follow(followed_user)
        db.session.commit()
        self.set_status(204)

    @authenticate(token_auth)
    @response(EmptySchema, status_code=204,
              description='User unfollowed successfully.')
    @other_responses({404: 'User not found', 409: 'User is not followed.'})
    def unfollow(self, id):
        """Unfollow a user"""
        user = token_auth.current_user()
        unfollowed_user = db.session.get(User, id)
        if not unfollowed_user:
            raise tornado.web.HTTPError(404)
        if not user.is_following(unfollowed_user):
            raise tornado.web.HTTPError(409)
        user.unfollow(unfollowed_user)
        db.session.commit()
        self.set_status(204)

    @authenticate(token_auth)
    @paginated_response(users_schema, order_by=User.username)
    @other_responses({404: 'User not found'})
    def following(self, id):
        """Retrieve the users this user is following"""
        user = db.session.get(User, id)
        if not user:
            raise tornado.web.HTTPError(404)
        self.write(user.following.select())

    @authenticate(token_auth)
    @paginated_response(users_schema, order_by=User.username)
    @other_responses({404: 'User not found'})
    def followers(self, id):
        """Retrieve the followers of the user"""
        user = db.session.get(User, id)
        if not user:
            raise tornado.web.HTTPError(404)
        self.write(user.followers.select())
