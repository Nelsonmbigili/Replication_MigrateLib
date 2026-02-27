import secrets
from urllib.parse import urlencode
import pycurl
import json
from io import BytesIO

from flask import Blueprint, request, abort, current_app, url_for, session
from werkzeug.http import dump_cookie
from apifairy import authenticate, body, response, other_responses

from api.app import db
from api.auth import basic_auth, token_auth
from api.email import send_email
from api.models import User, Token
from api.schemas import TokenSchema, PasswordResetRequestSchema, \
    PasswordResetSchema, OAuth2Schema, EmptySchema

tokens = Blueprint('tokens', __name__)
token_schema = TokenSchema()
oauth2_schema = OAuth2Schema()


def token_response(token):
    headers = {}
    if current_app.config['REFRESH_TOKEN_IN_COOKIE']:
        samesite = 'strict'
        if current_app.config['USE_CORS']:  # pragma: no branch
            samesite = 'none' if not current_app.debug else 'lax'
        headers['Set-Cookie'] = dump_cookie(
            'refresh_token', token.refresh_token,
            path=url_for('tokens.new'), secure=not current_app.debug,
            httponly=True, samesite=samesite)
    return {
        'access_token': token.access_token_jwt,
        'refresh_token': token.refresh_token
        if current_app.config['REFRESH_TOKEN_IN_BODY'] else None,
    }, 200, headers


@tokens.route('/tokens/oauth2/<provider>', methods=['POST'])
@body(oauth2_schema)
@response(token_schema)
@other_responses({401: 'Invalid code or state',
                  404: 'Unknown OAuth2 provider'})
def oauth2_new(args, provider):
    """Create new access and refresh tokens with OAuth2 authentication

    The refresh token is returned in the body of the request or as a hardened
    cookie, depending on configuration. A cookie should be used when the
    client is running in an insecure environment such as a web browser, and
    cannot adequately protect the refresh token against unauthorized access.
    """
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)
    if args['state'] != session.get('oauth2_state'):
        abort(401)

    # Perform POST request to get access token
    post_buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, provider_data['access_token_url'])
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, urlencode({
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': current_app.config['OAUTH2_REDIRECT_URI'].format(
            provider=provider),
    }))
    c.setopt(c.HTTPHEADER, ['Accept: application/json'])
    c.setopt(c.WRITEDATA, post_buffer)
    c.perform()
    status_code = c.getinfo(pycurl.RESPONSE_CODE)
    c.close()

    if status_code != 200:
        abort(401)

    post_response = json.loads(post_buffer.getvalue().decode('utf-8'))
    oauth2_token = post_response.get('access_token')
    if not oauth2_token:
        abort(401)

    # Perform GET request to fetch user information
    get_buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, provider_data['get_user']['url'])
    c.setopt(c.HTTPHEADER, [
        f'Authorization: Bearer {oauth2_token}',
        'Accept: application/json',
    ])
    c.setopt(c.WRITEDATA, get_buffer)
    c.perform()
    status_code = c.getinfo(pycurl.RESPONSE_CODE)
    c.close()

    if status_code != 200:
        abort(401)

    get_response = json.loads(get_buffer.getvalue().decode('utf-8'))
    email = provider_data['get_user']['email'](get_response)
    user = db.session.scalar(User.select().where(User.email == email))
    if user is None:
        user = User(email=email, username=email.split('@')[0])
        db.session.add(user)
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()  # keep token table clean of old tokens
    db.session.commit()
    return token_response(token)
