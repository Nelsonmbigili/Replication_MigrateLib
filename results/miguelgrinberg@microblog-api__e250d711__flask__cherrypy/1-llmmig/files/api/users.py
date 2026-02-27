import cherrypy
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


class UsersAPI:
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.tools.body(schema=user_schema)
    @cherrypy.tools.response(schema=user_schema, status=201)
    @cherrypy.expose
    def users(self, **kwargs):
        """Register a new user"""
        if cherrypy.request.method == 'POST':
            args = cherrypy.request.json
            user = User(**args)
            db.session.add(user)
            db.session.commit()
            return user
        elif cherrypy.request.method == 'GET':
            token_auth.authenticate()
            return User.select()

    @cherrypy.tools.json_out()
    @cherrypy.tools.authenticate(token_auth)
    @cherrypy.tools.response(schema=user_schema)
    @cherrypy.tools.other_responses({404: 'User not found'})
    @cherrypy.expose
    def user(self, id=None, username=None):
        """Retrieve a user by id or username"""
        if id is not None:
            user = db.session.get(User, id)
            if not user:
                raise cherrypy.HTTPError(404, 'User not found')
            return user
        elif username is not None:
            user = db.session.scalar(User.select().filter_by(username=username))
            if not user:
                raise cherrypy.HTTPError(404, 'User not found')
            return user

    @cherrypy.tools.json_out()
    @cherrypy.tools.authenticate(token_auth)
    @cherrypy.tools.response(schema=user_schema)
    @cherrypy.expose
    def me(self, **kwargs):
        """Retrieve the authenticated user"""
        if cherrypy.request.method == 'GET':
            return token_auth.current_user()
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            user = token_auth.current_user()
            if 'password' in data and ('old_password' not in data or
                                       not user.verify_password(data['old_password'])):
                raise cherrypy.HTTPError(400, 'Invalid password')
            user.update(data)
            db.session.commit()
            return user

    @cherrypy.tools.json_out()
    @cherrypy.tools.authenticate(token_auth)
    @cherrypy.tools.paginated_response(users_schema, order_by=User.username)
    @cherrypy.expose
    def my_following(self):
        """Retrieve the users the logged in user is following"""
        user = token_auth.current_user()
        return user.following.select()

    @cherrypy.tools.json_out()
    @cherrypy.tools.authenticate(token_auth)
    @cherrypy.tools.paginated_response(users_schema, order_by=User.username)
    @cherrypy.expose
    def my_followers(self):
        """Retrieve the followers of the logged in user"""
        user = token_auth.current_user()
        return user.followers.select()

    @cherrypy.tools.json_out()
    @cherrypy.tools.authenticate(token_auth)
    @cherrypy.tools.response(EmptySchema, status_code=204,
                              description='User is followed.')
    @cherrypy.tools.other_responses({404: 'User is not followed'})
    @cherrypy.expose
    def is_followed(self, id):
        """Check if a user is followed"""
        user = token_auth.current_user()
        followed_user = db.session.get(User, id)
        if not followed_user or not user.is_following(followed_user):
            raise cherrypy.HTTPError(404, 'User is not followed')
        return {}

    @cherrypy.tools.json_out()
    @cherrypy.tools.authenticate(token_auth)
    @cherrypy.tools.response(EmptySchema, status_code=204,
                              description='User followed successfully.')
    @cherrypy.tools.other_responses({404: 'User not found', 409: 'User already followed.'})
    @cherrypy.expose
    def follow(self, id):
        """Follow a user"""
        user = token_auth.current_user()
        followed_user = db.session.get(User, id)
        if not followed_user:
            raise cherrypy.HTTPError(404, 'User not found')
        if user.is_following(followed_user):
            raise cherrypy.HTTPError(409, 'User already followed')
        user.follow(followed_user)
        db.session.commit()
        return {}

    @cherrypy.tools.json_out()
    @cherrypy.tools.authenticate(token_auth)
    @cherrypy.tools.response(EmptySchema, status_code=204,
                              description='User unfollowed successfully.')
    @cherrypy.tools.other_responses({404: 'User not found', 409: 'User is not followed.'})
    @cherrypy.expose
    def unfollow(self, id):
        """Unfollow a user"""
        user = token_auth.current_user()
        unfollowed_user = db.session.get(User, id)
        if not unfollowed_user:
            raise cherrypy.HTTPError(404, 'User not found')
        if not user.is_following(unfollowed_user):
            raise cherrypy.HTTPError(409, 'User is not followed')
        user.unfollow(unfollowed_user)
        db.session.commit()
        return {}

    @cherrypy.tools.json_out()
    @cherrypy.tools.authenticate(token_auth)
    @cherrypy.tools.paginated_response(users_schema, order_by=User.username)
    @cherrypy.tools.other_responses({404: 'User not found'})
    @cherrypy.expose
    def following(self, id):
        """Retrieve the users this user is following"""
        user = db.session.get(User, id)
        if not user:
            raise cherrypy.HTTPError(404, 'User not found')
        return user.following.select()

    @cherrypy.tools.json_out()
    @cherrypy.tools.authenticate(token_auth)
    @cherrypy.tools.paginated_response(users_schema, order_by=User.username)
    @cherrypy.tools.other_responses({404: 'User not found'})
    @cherrypy.expose
    def followers(self, id):
        """Retrieve the followers of the user"""
        user = db.session.get(User, id)
        if not user:
            raise cherrypy.HTTPError(404, 'User not found')
        return user.followers.select()


if __name__ == '__main__':
    cherrypy.tree.mount(UsersAPI(), '/')
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.quickstart()
