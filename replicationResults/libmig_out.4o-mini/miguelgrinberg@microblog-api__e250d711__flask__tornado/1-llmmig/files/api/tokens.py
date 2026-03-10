import secrets
from urllib.parse import urlencode

from tornado.web import RequestHandler, Application
from tornado.ioloop import IOLoop
from apifairy import authenticate, body, response, other_responses
import requests

from api.app import db
from api.auth import basic_auth, token_auth
from api.email import send_email
from api.models import User, Token
from api.schemas import TokenSchema, PasswordResetRequestSchema, \
    PasswordResetSchema, OAuth2Schema, EmptySchema

token_schema = TokenSchema()
oauth2_schema = OAuth2Schema()


class TokenHandler(RequestHandler):
    def token_response(self, token):
        headers = {}
        if self.application.settings['REFRESH_TOKEN_IN_COOKIE']:
            samesite = 'strict'
            if self.application.settings['USE_CORS']:  # pragma: no branch
                samesite = 'none' if not self.application.debug else 'lax'
            headers['Set-Cookie'] = f'refresh_token={token.refresh_token}; Path=/tokens; HttpOnly; SameSite={samesite}; Secure={not self.application.debug}'
        return {
            'access_token': token.access_token_jwt,
            'refresh_token': token.refresh_token
            if self.application.settings['REFRESH_TOKEN_IN_BODY'] else None,
        }, 200, headers

    @authenticate(basic_auth)
    @response(token_schema)
    @other_responses({401: 'Invalid username or password'})
    def post(self):
        """Create new access and refresh tokens"""
        user = basic_auth.current_user()
        token = user.generate_auth_token()
        db.session.add(token)
        Token.clean()  # keep token table clean of old tokens
        db.session.commit()
        response, status_code, headers = self.token_response(token)
        self.set_status(status_code)
        for key, value in headers.items():
            self.set_header(key, value)
        self.write(response)

    @body(token_schema)
    @response(token_schema, description='Newly issued access and refresh tokens')
    @other_responses({401: 'Invalid access or refresh token'})
    def put(self):
        """Refresh an access token"""
        access_token_jwt = self.get_argument('access_token')
        refresh_token = self.get_argument('refresh_token', self.get_cookie('refresh_token'))
        if not access_token_jwt or not refresh_token:
            self.set_status(401)
            self.write({'error': 'Unauthorized'})
            return
        token = User.verify_refresh_token(refresh_token, access_token_jwt)
        if not token:
            self.set_status(401)
            self.write({'error': 'Unauthorized'})
            return
        token.expire()
        new_token = token.user.generate_auth_token()
        db.session.add_all([token, new_token])
        db.session.commit()
        response, status_code, headers = self.token_response(new_token)
        self.set_status(status_code)
        for key, value in headers.items():
            self.set_header(key, value)
        self.write(response)

    @authenticate(token_auth)
    @response(EmptySchema, status_code=204, description='Token revoked')
    @other_responses({401: 'Invalid access token'})
    def delete(self):
        """Revoke an access token"""
        access_token_jwt = self.request.headers['Authorization'].split()[1]
        token = Token.from_jwt(access_token_jwt)
        if not token:  # pragma: no cover
            self.set_status(401)
            self.write({'error': 'Unauthorized'})
            return
        token.expire()
        db.session.commit()
        self.set_status(204)

    @body(PasswordResetRequestSchema)
    @response(EmptySchema, status_code=204, description='Password reset email sent')
    def post_reset(self):
        """Request a password reset token"""
        user = db.session.scalar(User.select().filter_by(email=self.get_argument('email')))
        if user is not None:
            reset_token = user.generate_reset_token()
            reset_url = self.application.settings['PASSWORD_RESET_URL'] + \
                '?token=' + reset_token
            send_email(self.get_argument('email'), 'Reset Your Password', 'reset',
                       username=user.username, token=reset_token, url=reset_url)
        self.set_status(204)

    @body(PasswordResetSchema)
    @response(EmptySchema, status_code=204, description='Password reset successful')
    @other_responses({400: 'Invalid reset token'})
    def put_reset(self):
        """Reset a user password"""
        user = User.verify_reset_token(self.get_argument('token'))
        if user is None:
            self.set_status(400)
            self.write({'error': 'Invalid reset token'})
            return
        user.password = self.get_argument('new_password')
        db.session.commit()
        self.set_status(204)

    @response(EmptySchema, status_code=302, description="Redirect to OAuth2 provider's authentication page")
    @other_responses({404: 'Unknown OAuth2 provider'})
    def get_oauth2_authorize(self, provider):
        """Initiate OAuth2 authentication with a third-party provider"""
        provider_data = self.application.settings['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            self.set_status(404)
            self.write({'error': 'Unknown OAuth2 provider'})
            return
        self.application.settings['oauth2_state'] = secrets.token_urlsafe(16)
        qs = urlencode({
            'client_id': provider_data['client_id'],
            'redirect_uri': self.application.settings['OAUTH2_REDIRECT_URI'].format(provider=provider),
            'response_type': 'code',
            'scope': ' '.join(provider_data['scopes']),
            'state': self.application.settings['oauth2_state'],
        })
        self.set_status(302)
        self.set_header('Location', provider_data['authorize_url'] + '?' + qs)
        self.write({})

    @body(oauth2_schema)
    @response(token_schema)
    @other_responses({401: 'Invalid code or state', 404: 'Unknown OAuth2 provider'})
    def post_oauth2_new(self, provider):
        """Create new access and refresh tokens with OAuth2 authentication"""
        provider_data = self.application.settings['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            self.set_status(404)
            self.write({'error': 'Unknown OAuth2 provider'})
            return
        if self.get_argument('state') != self.application.settings.get('oauth2_state'):
            self.set_status(401)
            self.write({'error': 'Unauthorized'})
            return
        response = requests.post(provider_data['access_token_url'], data={
            'client_id': provider_data['client_id'],
            'client_secret': provider_data['client_secret'],
            'code': self.get_argument('code'),
            'grant_type': 'authorization_code',
            'redirect_uri': self.application.settings['OAUTH2_REDIRECT_URI'].format(provider=provider),
        }, headers={'Accept': 'application/json'})
        if response.status_code != 200:
            self.set_status(401)
            self.write({'error': 'Unauthorized'})
            return
        oauth2_token = response.json().get('access_token')
        if not oauth2_token:
            self.set_status(401)
            self.write({'error': 'Unauthorized'})
            return
        response = requests.get(provider_data['get_user']['url'], headers={
            'Authorization': 'Bearer ' + oauth2_token,
            'Accept': 'application/json',
        })
        if response.status_code != 200:
            self.set_status(401)
            self.write({'error': 'Unauthorized'})
            return
        email = provider_data['get_user']['email'](response.json())
        user = db.session.scalar(User.select().where(User.email == email))
        if user is None:
            user = User(email=email, username=email.split('@')[0])
            db.session.add(user)
        token = user.generate_auth_token()
        db.session.add(token)
        Token.clean()  # keep token table clean of old tokens
        db.session.commit()
        response, status_code, headers = self.token_response(token)
        self.set_status(status_code)
        for key, value in headers.items():
            self.set_header(key, value)
        self.write(response)


def make_app():
    return Application([
        (r"/tokens", TokenHandler),
        (r"/tokens/reset", TokenHandler),
        (r"/tokens/oauth2/(.*)", TokenHandler),
    ], debug=True, 
    settings={
        'REFRESH_TOKEN_IN_COOKIE': True,
        'USE_CORS': True,
        'PASSWORD_RESET_URL': 'http://example.com/reset',
        'OAUTH2_PROVIDERS': {
            # Add your OAuth2 providers here
        },
    })


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()
