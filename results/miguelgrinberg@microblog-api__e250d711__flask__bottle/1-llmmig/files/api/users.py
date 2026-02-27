from apifairy.decorators import other_responses
from bottle import Bottle, HTTPError
from apifairy import authenticate, body, response

from api import db
from api.models import User
from api.schemas import UserSchema, UpdateUserSchema, EmptySchema
from api.auth import token_auth
from api.decorators import paginated_response

app = Bottle()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
update_user_schema = UpdateUserSchema(partial=True)


@app.route('/users', method='POST')
@body(user_schema)
@response(user_schema, 201)
def new(args):
    """Register a new user"""
    user = User(**args)
    db.session.add(user)
    db.session.commit()
    return user


@app.route('/users', method='GET')
@authenticate(token_auth)
@paginated_response(users_schema)
def all():
    """Retrieve all users"""
    return User.select()


@app.route('/users/<id:int>', method='GET')
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get(id):
    """Retrieve a user by id"""
    return db.session.get(User, id) or HTTPError(404, 'User not found')


@app.route('/users/<username>', method='GET')
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get_by_username(username):
    """Retrieve a user by username"""
    return db.session.scalar(User.select().filter_by(username=username)) or \
        HTTPError(404, 'User not found')


@app.route('/me', method='GET')
@authenticate(token_auth)
@response(user_schema)
def me():
    """Retrieve the authenticated user"""
    return token_auth.current_user()


@app.route('/me', method='PUT')
@authenticate(token_auth)
@body(update_user_schema)
@response(user_schema)
def put(data):
    """Edit user information"""
    user = token_auth.current_user()
    if 'password' in data and ('old_password' not in data or
                               not user.verify_password(data['old_password'])):
        raise HTTPError(400, 'Invalid password')
    user.update(data)
    db.session.commit()
    return user


@app.route('/me/following', method='GET')
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
def my_following():
    """Retrieve the users the logged in user is following"""
    user = token_auth.current_user()
    return user.following.select()


@app.route('/me/followers', method='GET')
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
def my_followers():
    """Retrieve the followers of the logged in user"""
    user = token_auth.current_user()
    return user.followers.select()


@app.route('/me/following/<id:int>', method='GET')
@authenticate(token_auth)
@response(EmptySchema, status_code=204,
          description='User is followed.')
@other_responses({404: 'User is not followed'})
def is_followed(id):
    """Check if a user is followed"""
    user = token_auth.current_user()
    followed_user = db.session.get(User, id) or HTTPError(404, 'User not found')
    if not user.is_following(followed_user):
        raise HTTPError(404, 'User is not followed')
    return {}


@app.route('/me/following/<id:int>', method='POST')
@authenticate(token_auth)
@response(EmptySchema, status_code=204,
          description='User followed successfully.')
@other_responses({404: 'User not found', 409: 'User already followed.'})
def follow(id):
    """Follow a user"""
    user = token_auth.current_user()
    followed_user = db.session.get(User, id) or HTTPError(404, 'User not found')
    if user.is_following(followed_user):
        raise HTTPError(409, 'User already followed')
    user.follow(followed_user)
    db.session.commit()
    return {}


@app.route('/me/following/<id:int>', method='DELETE')
@authenticate(token_auth)
@response(EmptySchema, status_code=204,
          description='User unfollowed successfully.')
@other_responses({404: 'User not found', 409: 'User is not followed.'})
def unfollow(id):
    """Unfollow a user"""
    user = token_auth.current_user()
    unfollowed_user = db.session.get(User, id) or HTTPError(404, 'User not found')
    if not user.is_following(unfollowed_user):
        raise HTTPError(409, 'User is not followed')
    user.unfollow(unfollowed_user)
    db.session.commit()
    return {}


@app.route('/users/<id:int>/following', method='GET')
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
@other_responses({404: 'User not found'})
def following(id):
    """Retrieve the users this user is following"""
    user = db.session.get(User, id) or HTTPError(404, 'User not found')
    return user.following.select()


@app.route('/users/<id:int>/followers', method='GET')
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
@other_responses({404: 'User not found'})
def followers(id):
    """Retrieve the followers of the user"""
    user = db.session.get(User, id) or HTTPError(404, 'User not found')
    return user.followers.select()
