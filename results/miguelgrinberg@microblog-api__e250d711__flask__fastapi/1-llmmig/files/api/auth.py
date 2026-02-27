from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from api.app import app, db
from api.models import User

basic_auth = HTTPBasic()
token_auth = HTTPBearer()


def verify_password(credentials: HTTPBasicCredentials = Depends(basic_auth)):
    username = credentials.username
    password = credentials.password
    if username and password:
        user = db.session.scalar(User.select().filter_by(username=username))
        if user is None:
            user = db.session.scalar(User.select().filter_by(email=username))
        if user and user.verify_password(password):
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


def basic_auth_error():
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized access",
        headers={"WWW-Authenticate": "Basic"},
    )
    return JSONResponse(
        content={
            'code': error.status_code,
            'message': "Unauthorized",
            'description': error.detail,
        },
        status_code=error.status_code,
    )


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(token_auth)):
    access_token = credentials.credentials
    if app.state.DISABLE_AUTH:
        user = db.session.get(User, 1)
        user.ping()
        return user
    if access_token:
        user = User.verify_access_token(access_token)
        if user:
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def token_auth_error():
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized access",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return JSONResponse(
        content={
            'code': error.status_code,
            'message': "Unauthorized",
            'description': error.detail,
        },
        status_code=error.status_code,
    )
