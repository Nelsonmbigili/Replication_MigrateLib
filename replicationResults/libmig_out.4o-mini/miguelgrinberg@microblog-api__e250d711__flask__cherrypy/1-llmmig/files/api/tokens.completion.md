### Explanation of Changes

To migrate the provided Flask code to CherryPy, several key changes were made:

1. **Import Changes**: The `flask` and `werkzeug` imports were replaced with `cherrypy` and necessary modules for handling requests and responses.
2. **Blueprints**: CherryPy does not have a concept of Blueprints like Flask. Instead, we define a class to handle the routes.
3. **Request Handling**: The way requests and responses are handled differs between Flask and CherryPy. We replaced `request` and `abort` with CherryPy's `cherrypy.request` and `cherrypy.HTTPError`.
4. **Session Management**: CherryPy uses its own session management, so we replaced Flask's session handling with CherryPy's session handling.
5. **Response Handling**: The response format was adjusted to fit CherryPy's way of returning data, including setting headers directly in the response.

### Modified Code

```python
import secrets
from urllib.parse import urlencode

import cherrypy
from cherrypy.lib import sessions
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

class Tokens:
    @staticmethod
    def token_response(token):
        headers = {}
        if cherrypy.request.app.config['REFRESH_TOKEN_IN_COOKIE']:
            samesite = 'strict'
            if cherrypy.request.app.config['USE_CORS']:  # pragma: no branch
                samesite = 'none' if not cherrypy.request.app.debug else 'lax'
            headers['Set-Cookie'] = f'refresh_token={token.refresh_token}; Path=/tokens/new; Secure={not cherrypy.request.app.debug}; HttpOnly; SameSite={samesite}'
        return {
            'access_token': token.access_token_jwt,
            'refresh_token': token.refresh_token
            if cherrypy.request.app.config['REFRESH_TOKEN_IN_BODY'] else None,
        }, 200, headers

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @authenticate(basic_auth)
    @response(token_schema)
    @other_responses({401: 'Invalid username or password'})
    def new(self):
        """Create new access and refresh tokens"""
        user = basic_auth.current_user()
        token = user.generate_auth_token()
        db.session.add(token)
        Token.clean()  # keep token table clean of old tokens
        db.session.commit()
        return self.token_response(token)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @body(token_schema)
    @response(token_schema, description='Newly issued access and refresh tokens')
    @other_responses({401: 'Invalid access or refresh token'})
    def refresh(self):
        """Refresh an access token"""
        args = cherrypy.request.json
        access_token_jwt = args['access_token']
        refresh_token = args.get('refresh_token', cherrypy.request.cookies.get('refresh_token'))
        if not access_token_jwt or not refresh_token:
            raise cherrypy.HTTPError(401)
        token = User.verify_refresh_token(refresh_token, access_token_jwt)
        if not token:
            raise cherrypy.HTTPError(401)
        token.expire()
        new_token = token.user.generate_auth_token()
        db.session.add_all([token, new_token])
        db.session.commit()
        return self.token_response(new_token)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @authenticate(token_auth)
    @response(EmptySchema, status_code=204, description='Token revoked')
    @other_responses({401: 'Invalid access token'})
    def revoke(self):
        """Revoke an access token"""
        access_token_jwt = cherrypy.request.headers['Authorization'].split()[1]
        token = Token.from_jwt(access_token_jwt)
        if not token:  # pragma: no cover
            raise cherrypy.HTTPError(401)
        token.expire()
        db.session.commit()
        return {}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @body(PasswordResetRequestSchema)
    @response(EmptySchema, status_code=204, description='Password reset email sent')
    def reset(self):
        """Request a password reset token"""
        args = cherrypy.request.json
        user = db.session.scalar(User.select().filter_by(email=args['email']))
        if user is not None:
            reset_token = user.generate_reset_token()
            reset_url = cherrypy.request.app.config['PASSWORD_RESET_URL'] + \
                '?token=' + reset_token
            send_email(args['email'], 'Reset Your Password', 'reset',
                       username=user.username, token=reset_token, url=reset_url)
        return {}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @body(PasswordResetSchema)
    @response(EmptySchema, status_code=204, description='Password reset successful')
    @other_responses({400: 'Invalid reset token'})
    def password_reset(self):
        """Reset a user password"""
        args = cherrypy.request.json
        user = User.verify_reset_token(args['token'])
        if user is None:
            raise cherrypy.HTTPError(400)
        user.password = args['new_password']
        db.session.commit()
        return {}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @response(EmptySchema, status_code=302, description="Redirect to OAuth2 provider's authentication page")
    @other_responses({404: 'Unknown OAuth2 provider'})
    def oauth2_authorize(self, provider):
        """Initiate OAuth2 authentication with a third-party provider"""
        provider_data = cherrypy.request.app.config['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            raise cherrypy.HTTPError(404)
        sessions['oauth2_state'] = secrets.token_urlsafe(16)
        qs = urlencode({
            'client_id': provider_data['client_id'],
            'redirect_uri': cherrypy.request.app.config['OAUTH2_REDIRECT_URI'].format(provider=provider),
            'response_type': 'code',
            'scope': ' '.join(provider_data['scopes']),
            'state': sessions['oauth2_state'],
        })
        raise cherrypy.HTTPRedirect(provider_data['authorize_url'] + '?' + qs)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @body(oauth2_schema)
    @response(token_schema)
    @other_responses({401: 'Invalid code or state', 404: 'Unknown OAuth2 provider'})
    def oauth2_new(self, provider):
        """Create new access and refresh tokens with OAuth2 authentication"""
        provider_data = cherrypy.request.app.config['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            raise cherrypy.HTTPError(404)
        args = cherrypy.request.json
        if args['state'] != sessions.get('oauth2_state'):
            raise cherrypy.HTTPError(401)
        response = requests.post(provider_data['access_token_url'], data={
            'client_id': provider_data['client_id'],
            'client_secret': provider_data['client_secret'],
            'code': args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': cherrypy.request.app.config['OAUTH2_REDIRECT_URI'].format(provider=provider),
        }, headers={'Accept': 'application/json'})
        if response.status_code != 200:
            raise cherrypy.HTTPError(401)
        oauth2_token = response.json().get('access_token')
        if not oauth2_token:
            raise cherrypy.HTTPError(401)
        response = requests.get(provider_data['get_user']['url'], headers={
            'Authorization': 'Bearer ' + oauth2_token,
            'Accept': 'application/json',
        })
        if response.status_code != 200:
            raise cherrypy.HTTPError(401)
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

# To run the CherryPy application, you would typically do something like this:
# if __name__ == '__main__':
#     cherrypy.quickstart(Tokens())
``` 

This code now uses CherryPy to handle the same functionality that was previously implemented with Flask.