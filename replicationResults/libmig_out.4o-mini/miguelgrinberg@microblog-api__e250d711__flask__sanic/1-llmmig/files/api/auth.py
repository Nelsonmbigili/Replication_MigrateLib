from sanic import Sanic
from sanic.response import json
from sanic.exceptions import Unauthorized, Forbidden

from api.app import db
from api.models import User

app = Sanic("MyApp")

@app.middleware('request')
async def verify_password(request):
    username = request.headers.get('Authorization')
    password = request.headers.get('Password')
    if username and password:
        user = await db.session.scalar(User.select().filter_by(username=username))
        if user is None:
            user = await db.session.scalar(User.select().filter_by(email=username))
        if user and user.verify_password(password):
            request.user = user
            return

    raise Unauthorized("Invalid credentials")

@app.exception(Unauthorized)
async def basic_auth_error(request, exception):
    return json({
        'code': 401,
        'message': 'Unauthorized',
        'description': str(exception),
    }, status=401)

@app.middleware('request')
async def verify_token(request):
    access_token = request.headers.get('Authorization')
    if app.config['DISABLE_AUTH']:
        user = await db.session.get(User, 1)
        user.ping()
        request.user = user
        return
    if access_token:
        user = await User.verify_access_token(access_token)
        if user:
            request.user = user
            return

    raise Unauthorized("Invalid token")

@app.exception(Unauthorized)
async def token_auth_error(request, exception):
    return json({
        'code': 401,
        'message': 'Unauthorized',
        'description': str(exception),
    }, status=401)
