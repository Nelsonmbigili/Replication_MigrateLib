from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from apifairy import authenticate, body, response
from api import db
from api.models import User
from api.schemas import UserSchema, UpdateUserSchema, EmptySchema
from api.auth import token_auth
from api.decorators import paginated_response

app = FastAPI()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
update_user_schema = UpdateUserSchema(partial=True)


@app.post('/users', response_model=UserSchema, status_code=201)
@body(user_schema)
def new(args):
    """Register a new user"""
    user = User(**args)
    db.session.add(user)
    db.session.commit()
    return user


@app.get('/users', response_model=users_schema)
@authenticate(token_auth)
@paginated_response(users_schema)
def all():
    """Retrieve all users"""
    return User.select()


@app.get('/users/{id}', response_model=UserSchema)
@authenticate(token_auth)
@response(user_schema)
def get(id: int):
    """Retrieve a user by id"""
    user = db.session.get(User, id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get('/users/{username}', response_model=UserSchema)
@authenticate(token_auth)
@response(user_schema)
def get_by_username(username: str):
    """Retrieve a user by username"""
    user = db.session.scalar(User.select().filter_by(username=username))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get('/me', response_model=UserSchema)
@authenticate(token_auth)
@response(user_schema)
def me():
    """Retrieve the authenticated user"""
    return token_auth.current_user()


@app.put('/me', response_model=UserSchema)
@authenticate(token_auth)
@body(update_user_schema)
@response(user_schema)
def put(data):
    """Edit user information"""
    user = token_auth.current_user()
    if 'password' in data and ('old_password' not in data or
                               not user.verify_password(data['old_password'])):
        raise HTTPException(status_code=400, detail="Invalid password")
    user.update(data)
    db.session.commit()
    return user


@app.get('/me/following', response_model=users_schema)
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
def my_following():
    """Retrieve the users the logged in user is following"""
    user = token_auth.current_user()
    return user.following.select()


@app.get('/me/followers', response_model=users_schema)
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
def my_followers():
    """Retrieve the followers of the logged in user"""
    user = token_auth.current_user()
    return user.followers.select()


@app.get('/me/following/{id}', response_model=EmptySchema, status_code=204)
@authenticate(token_auth)
def is_followed(id: int):
    """Check if a user is followed"""
    user = token_auth.current_user()
    followed_user = db.session.get(User, id)
    if followed_user is None or not user.is_following(followed_user):
        raise HTTPException(status_code=404, detail="User is not followed")
    return {}


@app.post('/me/following/{id}', response_model=EmptySchema, status_code=204)
@authenticate(token_auth)
def follow(id: int):
    """Follow a user"""
    user = token_auth.current_user()
    followed_user = db.session.get(User, id)
    if followed_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_following(followed_user):
        raise HTTPException(status_code=409, detail="User already followed")
    user.follow(followed_user)
    db.session.commit()
    return {}


@app.delete('/me/following/{id}', response_model=EmptySchema, status_code=204)
@authenticate(token_auth)
def unfollow(id: int):
    """Unfollow a user"""
    user = token_auth.current_user()
    unfollowed_user = db.session.get(User, id)
    if unfollowed_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_following(unfollowed_user):
        raise HTTPException(status_code=409, detail="User is not followed")
    user.unfollow(unfollowed_user)
    db.session.commit()
    return {}


@app.get('/users/{id}/following', response_model=users_schema)
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
def following(id: int):
    """Retrieve the users this user is following"""
    user = db.session.get(User, id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user.following.select()


@app.get('/users/{id}/followers', response_model=users_schema)
@authenticate(token_auth)
@paginated_response(users_schema, order_by=User.username)
def followers(id: int):
    """Retrieve the followers of the user"""
    user = db.session.get(User, id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user.followers.select()
