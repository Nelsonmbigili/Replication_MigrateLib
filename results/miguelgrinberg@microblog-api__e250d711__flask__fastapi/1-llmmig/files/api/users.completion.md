### Explanation of Changes

To migrate the code from Flask to FastAPI, the following changes were made:

1. **Blueprint to Router**: Flask's `Blueprint` is replaced with FastAPI's `APIRouter`.
2. **Route Definitions**: Flask's `@users.route` decorator is replaced with FastAPI's `@router.get`, `@router.post`, etc., based on the HTTP method.
3. **Request and Response Handling**: FastAPI uses Pydantic models for request validation and response serialization. The `@body` and `@response` decorators from Flask are replaced with FastAPI's `request` and `response_model` parameters.
4. **Authentication**: The `@authenticate` decorator is replaced with FastAPI's dependency injection system using `Depends`.
5. **Error Handling**: Flask's `abort` is replaced with FastAPI's `HTTPException`.
6. **Other Responses**: FastAPI's `responses` parameter is used to define additional HTTP response codes.
7. **Paginated Responses**: The `@paginated_response` decorator is replaced with a custom dependency or function to handle pagination (assumed to be implemented elsewhere in the application).

Below is the modified code:

---

### Modified Code
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

from api import db
from api.models import User
from api.schemas import UserSchema, UpdateUserSchema, EmptySchema
from api.auth import token_auth
from api.decorators import paginated_response

router = APIRouter()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
update_user_schema = UpdateUserSchema(partial=True)


@router.post('/users', response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def new(args: UserSchema):
    """Register a new user"""
    user = User(**args.dict())
    db.session.add(user)
    db.session.commit()
    return user


@router.get('/users', response_model=List[UserSchema])
async def all(users=Depends(paginated_response), current_user=Depends(token_auth)):
    """Retrieve all users"""
    return User.select()


@router.get('/users/{id}', response_model=UserSchema, responses={404: {"description": "User not found"}})
async def get(id: int, current_user=Depends(token_auth)):
    """Retrieve a user by id"""
    user = db.session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get('/users/username/{username}', response_model=UserSchema, responses={404: {"description": "User not found"}})
async def get_by_username(username: str, current_user=Depends(token_auth)):
    """Retrieve a user by username"""
    user = db.session.scalar(User.select().filter_by(username=username))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get('/me', response_model=UserSchema)
async def me(current_user=Depends(token_auth)):
    """Retrieve the authenticated user"""
    return current_user


@router.put('/me', response_model=UserSchema)
async def put(data: UpdateUserSchema, current_user=Depends(token_auth)):
    """Edit user information"""
    user = current_user
    if 'password' in data.dict() and ('old_password' not in data.dict() or
                                      not user.verify_password(data.old_password)):
        raise HTTPException(status_code=400, detail="Invalid password")
    user.update(data.dict())
    db.session.commit()
    return user


@router.get('/me/following', response_model=List[UserSchema])
async def my_following(users=Depends(paginated_response), current_user=Depends(token_auth)):
    """Retrieve the users the logged in user is following"""
    user = current_user
    return user.following.select()


@router.get('/me/followers', response_model=List[UserSchema])
async def my_followers(users=Depends(paginated_response), current_user=Depends(token_auth)):
    """Retrieve the followers of the logged in user"""
    user = current_user
    return user.followers.select()


@router.get('/me/following/{id}', response_model=EmptySchema, responses={404: {"description": "User is not followed"}})
async def is_followed(id: int, current_user=Depends(token_auth)):
    """Check if a user is followed"""
    user = current_user
    followed_user = db.session.get(User, id)
    if not followed_user or not user.is_following(followed_user):
        raise HTTPException(status_code=404, detail="User is not followed")
    return {}


@router.post('/me/following/{id}', response_model=EmptySchema, responses={
    404: {"description": "User not found"},
    409: {"description": "User already followed"}
})
async def follow(id: int, current_user=Depends(token_auth)):
    """Follow a user"""
    user = current_user
    followed_user = db.session.get(User, id)
    if not followed_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_following(followed_user):
        raise HTTPException(status_code=409, detail="User already followed")
    user.follow(followed_user)
    db.session.commit()
    return {}


@router.delete('/me/following/{id}', response_model=EmptySchema, responses={
    404: {"description": "User not found"},
    409: {"description": "User is not followed"}
})
async def unfollow(id: int, current_user=Depends(token_auth)):
    """Unfollow a user"""
    user = current_user
    unfollowed_user = db.session.get(User, id)
    if not unfollowed_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_following(unfollowed_user):
        raise HTTPException(status_code=409, detail="User is not followed")
    user.unfollow(unfollowed_user)
    db.session.commit()
    return {}


@router.get('/users/{id}/following', response_model=List[UserSchema], responses={404: {"description": "User not found"}})
async def following(id: int, users=Depends(paginated_response), current_user=Depends(token_auth)):
    """Retrieve the users this user is following"""
    user = db.session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.following.select()


@router.get('/users/{id}/followers', response_model=List[UserSchema], responses={404: {"description": "User not found"}})
async def followers(id: int, users=Depends(paginated_response), current_user=Depends(token_auth)):
    """Retrieve the followers of the user"""
    user = db.session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.followers.select()
```

---

This code assumes that the `paginated_response` decorator and `token_auth` are adapted to work with FastAPI's dependency injection system.