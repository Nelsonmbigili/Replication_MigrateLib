import secrets
from urllib.parse import urlencode

from bottle import Bottle, request, abort, response, redirect
from werkzeug.http import dump_cookie
from apifairy import authenticate, body, response as apifairy_response
import requests

from api.app import db
from api.auth import basic_auth, token_auth
from api.email import send_email
from api.models import User, Token
from api.schemas import TokenSchema, PasswordResetRequestSchema, \
    PasswordResetSchema, OAuth2Schema, EmptySchema

app = Bottle()
token_schema = TokenSchema()
oauth2_schema = OAuth2Schema()


def token_response(token):
    if app.config['REFRESH_TOKEN_IN_COOKIE']:
        samesite = 'strict'
        if app.config['USE_CORS']:  # pragma: no branch
            samesite = 'none' if not app.debug else 'lax'
        response.set_cookie(
            'refresh_token', token.refresh_token,
            path=app.get_url('/tokens/new'), secure=not app.debug,
            httponly=True, samesite=samesite)
    return {
        'access_token': token.access_token_jwt,
        'refresh_token': token.refresh_token
        if app.config['REFRESH_TOKEN_IN_BODY'] else None,
    }


@app.post('/tokens')
@authenticate(basic_auth)
@apifairy_response(token_schema)
def new():
    """Create new access and refresh tokens"""
    user = basic_auth.current_user()
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()  # keep token table clean of old tokens
    db.session.commit()
    return token_response(token)


@app.put('/tokens')
@body(token_schema)
@apifairy_response(token_schema, description='Newly issued access and refresh tokens')
def refresh(args):
    """Refresh an access token"""
    access_token_jwt = args['access_token']
    refresh_token = args.get('refresh_token', request.get_cookie('refresh_token'))
    if not access_token_jwt or not refresh_token:
        abort(401)
    token = User.verify_refresh_token(refresh_token, access_token_jwt)
    if not token:
        abort(401)
    token.expire()
    new_token = token.user.generate_auth_token()
    db.session.add_all([token, new_token])
    db.session.commit()
    return token_response(new_token)


@app.delete('/tokens')
@authenticate(token_auth)
@apifairy_response(EmptySchema, status_code=204, description='Token revoked')
def revoke():
    """Revoke an access token"""
    access_token_jwt = request.headers['Authorization'].split()[1]
    token = Token.from_jwt(access_token_jwt)
    if not token:  # pragma: no cover
        abort(401)
    token.expire()
    db.session.commit()
    return {}


@app.post('/tokens/reset')
@body(PasswordResetRequestSchema)
@apifairy_response(EmptySchema, status_code=204, description='Password reset email sent')
def reset(args):
    """Request a password reset token"""
    user = db.session.scalar(User.select().filter_by(email=args['email']))
    if user is not None:
        reset_token = user.generate_reset_token()
        reset_url = app.config['PASSWORD_RESET_URL'] + '?token=' + reset_token
        send_email(args['email'], 'Reset Your Password', 'reset',
                   username=user.username, token=reset_token, url=reset_url)
    return {}


@app.put('/tokens/reset')
@body(PasswordResetSchema)
@apifairy_response(EmptySchema, status_code=204, description='Password reset successful')
def password_reset(args):
    """Reset a user password"""
    user = User.verify_reset_token(args['token'])
    if user is None:
        abort(400)
    user.password = args['new_password']
    db.session.commit()
    return {}


@app.get('/tokens/oauth2/<provider>')
@apifairy_response(EmptySchema, status_code=302, description="Redirect to OAuth2 provider's authentication page")
def oauth2_authorize(provider):
    """Initiate OAuth2 authentication with a third-party provider"""
    provider_data = app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)
    session = request.environ.get('beaker.session')
    session['oauth2_state'] = secrets.token_urlsafe(16)
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': app.config['OAUTH2_REDIRECT_URI'].format(provider=provider),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })
    redirect(provider_data['authorize_url'] + '?' + qs)


@app.post('/tokens/oauth2/<provider>')
@body(oauth2_schema)
@apifairy_response(token_schema)
def oauth2_new(args, provider):
    """Create new access and refresh tokens with OAuth2 authentication"""
    provider_data = app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)
    session = request.environ.get('beaker.session')
    if args['state'] != session.get('oauth2_state'):
        abort(401)
    response = requests.post(provider_data['access_token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': app.config['OAUTH2_REDIRECT_URI'].format(provider=provider),
    }, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)
    response = requests.get(provider_data['get_user']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    email = provider_data['get_user']['email'](response.json())
    user = db.session.scalar(User.select().where(User.email == email))
    if user is None:
        user = User(email=email, username=email.split('@')[0])
        db.session.add(user)
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()  # keep token table clean of old tokens
    db.session.commit()
    return token_response(token)
