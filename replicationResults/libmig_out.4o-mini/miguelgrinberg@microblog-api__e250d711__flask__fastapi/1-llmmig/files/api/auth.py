from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.app import db
from api.models import User

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(username: str, password: str):
    if username and password:
        user = db.session.scalar(User.select().filter_by(username=username))
        if user is None:
            user = db.session.scalar(User.select().filter_by(email=username))
        if user and user.verify_password(password):
            return user
    return None


def basic_auth_error(status: int):
    if status == 403:
        raise HTTPException(status_code=status, detail="Forbidden")
    else:
        raise HTTPException(status_code=status, detail="Unauthorized")


def verify_token(access_token: str = Depends(oauth2_scheme)):
    if app.state.DISABLE_AUTH:
        user = db.session.get(User, 1)
        user.ping()
        return user
    if access_token:
        return User.verify_access_token(access_token)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def token_auth_error(status: int):
    if status == 403:
        raise HTTPException(status_code=status, detail="Forbidden")
    else:
        raise HTTPException(status_code=status, detail="Unauthorized")
