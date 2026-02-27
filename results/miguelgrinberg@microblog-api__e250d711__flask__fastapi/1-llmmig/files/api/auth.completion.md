### Explanation of Changes
To migrate the code from Flask to FastAPI, the following changes were made:
1. **Authentication Handling**:
   - Flask's `HTTPBasicAuth` and `HTTPTokenAuth` were replaced with FastAPI's dependency injection mechanism using `Depends`.
   - Custom authentication functions were implemented to handle basic authentication and token authentication.
2. **Error Handling**:
   - Flask's `error_handler` methods were replaced with FastAPI's `HTTPException` for raising errors with appropriate status codes and messages.
3. **Request Context**:
   - Flask's `current_app` was replaced with FastAPI's `app.state` for accessing application-level configuration.
4. **Response Format**:
   - Flask's tuple-based response format was replaced with FastAPI's dictionary-based response using `JSONResponse`.

### Modified Code
```python
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
```

### Key Notes
- The `verify_password` and `verify_token` functions are now used as dependencies in FastAPI routes where authentication is required.
- The `basic_auth_error` and `token_auth_error` functions are not directly used in FastAPI but are included for consistency and can be used to return custom error responses if needed.
- FastAPI's `Depends` is used to inject authentication logic into routes, replacing Flask's decorators.