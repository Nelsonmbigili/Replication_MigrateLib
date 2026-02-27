import os
from environs import Env

env = Env()
env.read_env()  # Automatically loads environment variables from a .env file if it exists
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # database options
    ALCHEMICAL_DATABASE_URL = env.str('DATABASE_URL', default='sqlite:///' + os.path.join(basedir, 'db.sqlite'))
    ALCHEMICAL_ENGINE_OPTIONS = {'echo': env.bool('SQL_ECHO', default=False)}

    # security options
    SECRET_KEY = env.str('SECRET_KEY', default='top-secret!')
    DISABLE_AUTH = env.bool('DISABLE_AUTH', default=False)
    ACCESS_TOKEN_MINUTES = env.int('ACCESS_TOKEN_MINUTES', default=15)
    REFRESH_TOKEN_DAYS = env.int('REFRESH_TOKEN_DAYS', default=7)
    REFRESH_TOKEN_IN_COOKIE = env.bool('REFRESH_TOKEN_IN_COOKIE', default=True)
    REFRESH_TOKEN_IN_BODY = env.bool('REFRESH_TOKEN_IN_BODY', default=False)
    RESET_TOKEN_MINUTES = env.int('RESET_TOKEN_MINUTES', default=15)
    PASSWORD_RESET_URL = env.str('PASSWORD_RESET_URL', default='http://localhost:3000/reset')
    USE_CORS = env.bool('USE_CORS', default=True)
    CORS_SUPPORTS_CREDENTIALS = True
    OAUTH2_PROVIDERS = {
        # https://developers.google.com/identity/protocols/oauth2/web-server
        # #httprest
        'google': {
            'client_id': env.str('GOOGLE_CLIENT_ID', default=None),
            'client_secret': env.str('GOOGLE_CLIENT_SECRET', default=None),
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
            'access_token_url': 'https://accounts.google.com/o/oauth2/token',
            'get_user': {
                'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
                'email': lambda json: json['email'],
            },
            'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
        },
        # https://docs.github.com/en/apps/oauth-apps/building-oauth-apps
        # /authorizing-oauth-apps
        'github': {
            'client_id': env.str('GITHUB_CLIENT_ID', default=None),
            'client_secret': env.str('GITHUB_CLIENT_SECRET', default=None),
            'authorize_url': 'https://github.com/login/oauth/authorize',
            'access_token_url': 'https://github.com/login/oauth/access_token',
            'get_user': {
                'url': 'https://api.github.com/user/emails',
                'email': lambda json: json[0]['email'],
            },
            'scopes': ['user:email'],
        },
    }
    OAUTH2_REDIRECT_URI = env.str('OAUTH2_REDIRECT_URI', default='http://localhost:3000/oauth2/{provider}/callback')

    # API documentation
    APIFAIRY_TITLE = 'Microblog API'
    APIFAIRY_VERSION = '1.0'
    APIFAIRY_UI = env.str('DOCS_UI', default='elements')
    APIFAIRY_TAGS = ['tokens', 'users', 'posts']

    # email options
    MAIL_SERVER = env.str('MAIL_SERVER', default='localhost')
    MAIL_PORT = env.int('MAIL_PORT', default=25)
    MAIL_USE_TLS = env.bool('MAIL_USE_TLS', default=False)
    MAIL_USERNAME = env.str('MAIL_USERNAME', default=None)
    MAIL_PASSWORD = env.str('MAIL_PASSWORD', default=None)
    MAIL_DEFAULT_SENDER = env.str('MAIL_DEFAULT_SENDER', default='donotreply@microblog.example.com')
