import secrets
from urllib.parse import urlencode

import cherrypy
from werkzeug.http import dump_cookie
import requests

from api.app import db
from api.auth import basic_auth, token_auth
from api.email import send_email
from api.models import User, Token
from api.schemas import TokenSchema, PasswordResetRequestSchema, \
    PasswordResetSchema, OAuth2Schema, EmptySchema

token_schema = TokenSchema()
oauth2_schema = OAuth2Schema()


class TokenService:
    @staticmethod
    def token_response(token):
        headers = {}
        if cherrypy.config.get('REFRESH_TOKEN_IN_COOKIE'):
            samesite = 'strict'
            if cherrypy.config.get('USE_CORS'):  # pragma: no branch
                samesite = 'none' if not cherrypy.config.get('debug') else 'lax'
            cherrypy.response.cookie['refresh_token'] = token.refresh_token
            cherrypy.response.cookie['refresh_token']['path'] = '/tokens/new'
            cherrypy.response.cookie['refresh_token']['secure'] = not cherrypy.config.get('debug')
            cherrypy.response.cookie['refresh_token']['httponly'] = True
            cherrypy.response.cookie['refresh_token']['samesite'] = samesite
        return {
            'access_token': token.access_token_jwt,
            'refresh_token': token.refresh_token
            if cherrypy.config.get('REFRESH_TOKEN_IN_BODY') else None,
        }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def new(self):
        """Create new access and refresh tokens"""
        user = basic_auth.current_user()
        token = user.generate_auth_token()
        db.session.add(token)
        Token.clean()  # keep token table clean of old tokens
        db.session.commit()
        return self.token_response(token)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def refresh(self):
        """Refresh an access token"""
        args = cherrypy.request.json
        access_token_jwt = args['access_token']
        refresh_token = args.get('refresh_token', cherrypy.request.cookie.get('refresh_token'))
        if not access_token_jwt or not refresh_token:
            raise cherrypy.HTTPError(401, 'Invalid access or refresh token')
        token = User.verify_refresh_token(refresh_token, access_token_jwt)
        if not token:
            raise cherrypy.HTTPError(401, 'Invalid access or refresh token')
        token.expire()
        new_token = token.user.generate_auth_token()
        db.session.add_all([token, new_token])
        db.session.commit()
        return self.token_response(new_token)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def revoke(self):
        """Revoke an access token"""
        auth_header = cherrypy.request.headers.get('Authorization')
        if not auth_header:
            raise cherrypy.HTTPError(401, 'Invalid access token')
        access_token_jwt = auth_header.split()[1]
        token = Token.from_jwt(access_token_jwt)
        if not token:  # pragma: no cover
            raise cherrypy.HTTPError(401, 'Invalid access token')
        token.expire()
        db.session.commit()
        return {}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def reset(self):
        """Request a password reset token"""
        args = cherrypy.request.json
        user = db.session.scalar(User.select().filter_by(email=args['email']))
        if user is not None:
            reset_token = user.generate_reset_token()
            reset_url = cherrypy.config.get('PASSWORD_RESET_URL') + '?token=' + reset_token
            send_email(args['email'], 'Reset Your Password', 'reset',
                       username=user.username, token=reset_token, url=reset_url)
        return {}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def password_reset(self):
        """Reset a user password"""
        args = cherrypy.request.json
        user = User.verify_reset_token(args['token'])
        if user is None:
            raise cherrypy.HTTPError(400, 'Invalid reset token')
        user.password = args['new_password']
        db.session.commit()
        return {}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def oauth2_authorize(self, provider):
        """Initiate OAuth2 authentication with a third-party provider"""
        provider_data = cherrypy.config.get('OAUTH2_PROVIDERS', {}).get(provider)
        if provider_data is None:
            raise cherrypy.HTTPError(404, 'Unknown OAuth2 provider')
        cherrypy.session['oauth2_state'] = secrets.token_urlsafe(16)
        qs = urlencode({
            'client_id': provider_data['client_id'],
            'redirect_uri': cherrypy.config.get('OAUTH2_REDIRECT_URI').format(provider=provider),
            'response_type': 'code',
            'scope': ' '.join(provider_data['scopes']),
            'state': cherrypy.session['oauth2_state'],
        })
        cherrypy.response.status = 302
        cherrypy.response.headers['Location'] = provider_data['authorize_url'] + '?' + qs
        return {}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def oauth2_new(self, provider):
        """Create new access and refresh tokens with OAuth2 authentication"""
        args = cherrypy.request.json
        provider_data = cherrypy.config.get('OAUTH2_PROVIDERS', {}).get(provider)
        if provider_data is None:
            raise cherrypy.HTTPError(404, 'Unknown OAuth2 provider')
        if args['state'] != cherrypy.session.get('oauth2_state'):
            raise cherrypy.HTTPError(401, 'Invalid code or state')
        response = requests.post(provider_data['access_token_url'], data={
            'client_id': provider_data['client_id'],
            'client_secret': provider_data['client_secret'],
            'code': args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': cherrypy.config.get('OAUTH2_REDIRECT_URI').format(provider=provider),
        }, headers={'Accept': 'application/json'})
        if response.status_code != 200:
            raise cherrypy.HTTPError(401, 'Invalid code or state')
        oauth2_token = response.json().get('access_token')
        if not oauth2_token:
            raise cherrypy.HTTPError(401, 'Invalid code or state')
        response = requests.get(provider_data['get_user']['url'], headers={
            'Authorization': 'Bearer ' + oauth2_token,
            'Accept': 'application/json',
        })
        if response.status_code != 200:
            raise cherrypy.HTTPError(401, 'Invalid code or state')
        email = provider_data['get_user']['email'](response.json())
        user = db.session.scalar(User.select().where(User.email == email))
        if user is None:
            user = User(email=email, username=email.split('@')[0])
            db.session.add(user)
        token = user.generate_auth_token()
        db.session.add(token)
        Token.clean()  # keep token table clean of old tokens
        db.session.commit()
        return self.token_response(token)


if __name__ == '__main__':
@tokens.route('/tokens', methods=['POST'])
@authenticate(basic_auth)
@response(token_schema)
@other_responses({401: 'Invalid username or password'})
def new():
    """Create new access and refresh tokens

    The refresh token is returned in the body of the request or as a hardened
    cookie, depending on configuration. A cookie should be used when the
    client is running in an insecure environment such as a web browser, and
    cannot adequately protect the refresh token against unauthorized access.
    """
    user = basic_auth.current_user()
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()  # keep token table clean of old tokens
    db.session.commit()
    return token_response(token)


@tokens.route('/tokens', methods=['PUT'])
@body(token_schema)
@response(token_schema, description='Newly issued access and refresh tokens')
@other_responses({401: 'Invalid access or refresh token'})
def refresh(args):
    """Refresh an access token

    The client has the option to pass the refresh token in the body of the
    request or in a `refresh_token` cookie. The access token must be passed in
    the body of the request.
    """
    access_token_jwt = args['access_token']
    refresh_token = args.get('refresh_token', request.cookies.get(
        'refresh_token'))
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


@tokens.route('/tokens', methods=['DELETE'])
@authenticate(token_auth)
@response(EmptySchema, status_code=204, description='Token revoked')
@other_responses({401: 'Invalid access token'})
def revoke():
    """Revoke an access token"""
    access_token_jwt = request.headers['Authorization'].split()[1]
    token = Token.from_jwt(access_token_jwt)
    if not token:  # pragma: no cover
        abort(401)
    token.expire()
    db.session.commit()
    return {}


@tokens.route('/tokens/reset', methods=['POST'])
@body(PasswordResetRequestSchema)
@response(EmptySchema, status_code=204,
          description='Password reset email sent')
def reset(args):
    """Request a password reset token"""
    user = db.session.scalar(User.select().filter_by(email=args['email']))
    if user is not None:
        reset_token = user.generate_reset_token()
        reset_url = current_app.config['PASSWORD_RESET_URL'] + \
            '?token=' + reset_token
        send_email(args['email'], 'Reset Your Password', 'reset',
                   username=user.username, token=reset_token, url=reset_url)
    return {}


@tokens.route('/tokens/reset', methods=['PUT'])
@body(PasswordResetSchema)
@response(EmptySchema, status_code=204,
          description='Password reset successful')
@other_responses({400: 'Invalid reset token'})
def password_reset(args):
    """Reset a user password"""
    user = User.verify_reset_token(args['token'])
    if user is None:
        abort(400)
    user.password = args['new_password']
    db.session.commit()
    return {}


@tokens.route('/tokens/oauth2/<provider>', methods=['GET'])
@response(EmptySchema, status_code=302,
          description="Redirect to OAuth2 provider's authentication page")
@other_responses({404: 'Unknown OAuth2 provider'})
def oauth2_authorize(provider):
    """Initiate OAuth2 authentication with a third-party provider"""
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)
    session['oauth2_state'] = secrets.token_urlsafe(16)
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': current_app.config['OAUTH2_REDIRECT_URI'].format(
            provider=provider),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    cherrypy.tree.mount(TokenService(), '/tokens', {
        '/': {
            'tools.sessions.on': True,
            'tools.json_in.on': True,
            'tools.json_out.on': True,
        }
    })
    cherrypy.engine.start()
    return {}, 302, {'Location': provider_data['authorize_url'] + '?' + qs}


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
    response = requests.post(provider_data['access_token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': current_app.config['OAUTH2_REDIRECT_URI'].format(
            provider=provider),
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
    cherrypy.engine.block()