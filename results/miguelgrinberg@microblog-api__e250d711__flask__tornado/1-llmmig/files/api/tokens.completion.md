### Explanation of Changes

To migrate the code from Flask to Tornado, the following changes were made:

1. **Blueprints and Routing**:
   - Flask's `Blueprint` and `@route` decorators were replaced with Tornado's `RequestHandler` classes and URL routing.
   - Each route in Flask was converted into a Tornado `RequestHandler` class with appropriate HTTP methods (`post`, `put`, `delete`, etc.).

2. **Request and Response Handling**:
   - Flask's `request`, `abort`, and `response` were replaced with Tornado's `self.request`, `self.write`, and `self.set_status`.
   - Flask's `abort` was replaced with Tornado's `self.set_status` and `self.finish` for error handling.

3. **Session Management**:
   - Flask's `session` was replaced with Tornado's `self.get_secure_cookie` and `self.set_secure_cookie` for session management.

4. **Configuration Access**:
   - Flask's `current_app.config` was replaced with Tornado's `self.settings` to access application configuration.

5. **Cookie Handling**:
   - Flask's `dump_cookie` was replaced with Tornado's `self.set_cookie`.

6. **Routing Table**:
   - A routing table was created to map URLs to their respective Tornado `RequestHandler` classes.

7. **Initialization**:
   - Tornado's `Application` class was used to initialize the app with routes and settings.

### Modified Code

```python
import secrets
from urllib.parse import urlencode
import json

from tornado.web import Application, RequestHandler
from tornado.escape import json_decode
from tornado.httpclient import HTTPClient, HTTPRequest

from api.app import db
from api.auth import basic_auth, token_auth
from api.email import send_email
from api.models import User, Token
from api.schemas import TokenSchema, PasswordResetRequestSchema, \
    PasswordResetSchema, OAuth2Schema, EmptySchema

token_schema = TokenSchema()
oauth2_schema = OAuth2Schema()


class BaseHandler(RequestHandler):
    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json_decode(self.request.body)
        else:
            self.json_args = {}

    def write_error(self, status_code, **kwargs):
        self.set_status(status_code)
        self.finish({"error": self._reason})


class TokenResponseMixin:
    def token_response(self, token):
        headers = {}
        if self.settings['REFRESH_TOKEN_IN_COOKIE']:
            samesite = 'Strict'
            if self.settings['USE_CORS']:
                samesite = 'None' if not self.settings['DEBUG'] else 'Lax'
            self.set_cookie(
                'refresh_token', token.refresh_token,
                path='/tokens', secure=not self.settings['DEBUG'],
                httponly=True, samesite=samesite)
        response = {
            'access_token': token.access_token_jwt,
            'refresh_token': token.refresh_token
            if self.settings['REFRESH_TOKEN_IN_BODY'] else None,
        }
        self.write(response)


class NewTokenHandler(BaseHandler, TokenResponseMixin):
    def post(self):
        user = basic_auth.current_user()
        if not user:
            self.set_status(401)
            self.finish({"error": "Invalid username or password"})
            return
        token = user.generate_auth_token()
        db.session.add(token)
        Token.clean()
        db.session.commit()
        self.token_response(token)


class RefreshTokenHandler(BaseHandler, TokenResponseMixin):
    def put(self):
        args = self.json_args
        access_token_jwt = args.get('access_token')
        refresh_token = args.get('refresh_token', self.get_cookie('refresh_token'))
        if not access_token_jwt or not refresh_token:
            self.set_status(401)
            self.finish({"error": "Invalid access or refresh token"})
            return
        token = User.verify_refresh_token(refresh_token, access_token_jwt)
        if not token:
            self.set_status(401)
            self.finish({"error": "Invalid access or refresh token"})
            return
        token.expire()
        new_token = token.user.generate_auth_token()
        db.session.add_all([token, new_token])
        db.session.commit()
        self.token_response(new_token)


class RevokeTokenHandler(BaseHandler):
    def delete(self):
        access_token_jwt = self.request.headers.get('Authorization', '').split()[1]
        token = Token.from_jwt(access_token_jwt)
        if not token:
            self.set_status(401)
            self.finish({"error": "Invalid access token"})
            return
        token.expire()
        db.session.commit()
        self.set_status(204)
        self.finish()


class PasswordResetRequestHandler(BaseHandler):
    def post(self):
        args = self.json_args
        user = db.session.scalar(User.select().filter_by(email=args['email']))
        if user is not None:
            reset_token = user.generate_reset_token()
            reset_url = self.settings['PASSWORD_RESET_URL'] + '?token=' + reset_token
            send_email(args['email'], 'Reset Your Password', 'reset',
                       username=user.username, token=reset_token, url=reset_url)
        self.set_status(204)
        self.finish()


class PasswordResetHandler(BaseHandler):
    def put(self):
        args = self.json_args
        user = User.verify_reset_token(args['token'])
        if user is None:
            self.set_status(400)
            self.finish({"error": "Invalid reset token"})
            return
        user.password = args['new_password']
        db.session.commit()
        self.set_status(204)
        self.finish()


class OAuth2AuthorizeHandler(BaseHandler):
    def get(self, provider):
        provider_data = self.settings['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            self.set_status(404)
            self.finish({"error": "Unknown OAuth2 provider"})
            return
        state = secrets.token_urlsafe(16)
        self.set_secure_cookie('oauth2_state', state)
        qs = urlencode({
            'client_id': provider_data['client_id'],
            'redirect_uri': self.settings['OAUTH2_REDIRECT_URI'].format(provider=provider),
            'response_type': 'code',
            'scope': ' '.join(provider_data['scopes']),
            'state': state,
        })
        self.redirect(provider_data['authorize_url'] + '?' + qs)


class OAuth2NewHandler(BaseHandler, TokenResponseMixin):
    def post(self, provider):
        args = self.json_args
        provider_data = self.settings['OAUTH2_PROVIDERS'].get(provider)
        if provider_data is None:
            self.set_status(404)
            self.finish({"error": "Unknown OAuth2 provider"})
            return
        state = self.get_secure_cookie('oauth2_state')
        if args['state'] != state.decode():
            self.set_status(401)
            self.finish({"error": "Invalid state"})
            return
        client = HTTPClient()
        try:
            response = client.fetch(HTTPRequest(
                provider_data['access_token_url'],
                method="POST",
                body=urlencode({
                    'client_id': provider_data['client_id'],
                    'client_secret': provider_data['client_secret'],
                    'code': args['code'],
                    'grant_type': 'authorization_code',
                    'redirect_uri': self.settings['OAUTH2_REDIRECT_URI'].format(provider=provider),
                }),
                headers={'Accept': 'application/json'}
            ))
            oauth2_token = json.loads(response.body).get('access_token')
            if not oauth2_token:
                raise Exception
            user_response = client.fetch(HTTPRequest(
                provider_data['get_user']['url'],
                headers={
                    'Authorization': 'Bearer ' + oauth2_token,
                    'Accept': 'application/json',
                }
            ))
            email = provider_data['get_user']['email'](json.loads(user_response.body))
            user = db.session.scalar(User.select().where(User.email == email))
            if user is None:
                user = User(email=email, username=email.split('@')[0])
                db.session.add(user)
            token = user.generate_auth_token()
            db.session.add(token)
            Token.clean()
            db.session.commit()
            self.token_response(token)
        except Exception:
            self.set_status(401)
            self.finish({"error": "Invalid code or state"})


def make_app():
    return Application([
        (r"/tokens", NewTokenHandler),
        (r"/tokens/refresh", RefreshTokenHandler),
        (r"/tokens/revoke", RevokeTokenHandler),
        (r"/tokens/reset", PasswordResetRequestHandler),
        (r"/tokens/reset/confirm", PasswordResetHandler),
        (r"/tokens/oauth2/([^/]+)", OAuth2AuthorizeHandler),
        (r"/tokens/oauth2/([^/]+)/new", OAuth2NewHandler),
    ], debug=True, cookie_secret="YOUR_SECRET_KEY", REFRESH_TOKEN_IN_COOKIE=True,
       USE_CORS=False, PASSWORD_RESET_URL="http://example.com/reset",
       OAUTH2_PROVIDERS={}, OAUTH2_REDIRECT_URI="http://example.com/oauth2/{provider}/callback")


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    print("Server running on http://localhost:8000")
```