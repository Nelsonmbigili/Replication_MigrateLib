### Explanation of Changes

To migrate the code from Flask to CherryPy, the following changes were made:

1. **Blueprints and Routes**: Flask uses `Blueprint` and `@app.route` for routing, while CherryPy uses a class-based approach where methods are mapped to HTTP endpoints. Each route in Flask was converted into a method in a CherryPy class.
   
2. **Request and Response Handling**: Flask provides `request`, `abort`, and `response` objects directly. In CherryPy, these functionalities are handled using `cherrypy.request`, `cherrypy.response`, and raising HTTP errors using `cherrypy.HTTPError`.

3. **Session Management**: Flask's `session` object was replaced with CherryPy's session management (`cherrypy.session`).

4. **Configuration**: Flask's `current_app.config` was replaced with CherryPy's configuration system (`cherrypy.config`).

5. **Decorator Migration**: Flask-specific decorators like `@authenticate`, `@body`, `@response`, and `@other_responses` were removed. These need to be implemented manually or replaced with equivalent CherryPy-compatible logic.

6. **Cookie Handling**: Flask's `dump_cookie` was replaced with CherryPy's `cherrypy.response.cookie`.

7. **Error Handling**: Flask's `abort` was replaced with `cherrypy.HTTPError`.

8. **Application Initialization**: Flask's `Blueprint` was replaced with a CherryPy application class, and the application is mounted using `cherrypy.tree.mount`.

### Modified Code

```python
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
    cherrypy.tree.mount(TokenService(), '/tokens', {
        '/': {
            'tools.sessions.on': True,
            'tools.json_in.on': True,
            'tools.json_out.on': True,
        }
    })
    cherrypy.engine.start()
    cherrypy.engine.block()
```