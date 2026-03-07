import os
from dynaconf import settings

basedir = os.path.abspath(os.path.dirname(__file__))


def as_bool(value):
    if value:
        return value.lower() in ['true', 'yes', 'on', '1']
    return False


class Config:
    # database options
    ALCHEMICAL_DATABASE_URL = settings.DATABASE_URL or \
        'sqlite:///' + os.path.join(basedir, 'db.sqlite')
    ALCHEMICAL_ENGINE_OPTIONS = {'echo': as_bool(settings.SQL_ECHO)}

    # security options
    SECRET_KEY = settings.SECRET_KEY or 'top-secret!'
    DISABLE_AUTH = as_bool(settings.DISABLE_AUTH)
    ACCESS_TOKEN_MINUTES = int(settings.ACCESS_TOKEN_MINUTES or '15')
    REFRESH_TOKEN_DAYS = int(settings.REFRESH_TOKEN_DAYS or '7')
    REFRESH_TOKEN_IN_COOKIE = as_bool(settings.REFRESH_TOKEN_IN_COOKIE or 'yes')
    REFRESH_TOKEN_IN_BODY = as_bool(settings.REFRESH_TOKEN_IN_BODY)
    RESET_TOKEN_MINUTES = int(settings.RESET_TOKEN_MINUTES or '15')
    PASSWORD_RESET_URL = settings.PASSWORD_RESET_URL or \
        'http://localhost:3000/reset'
    USE_CORS = as_bool(settings.USE_CORS or 'yes')
    CORS_SUPPORTS_CREDENTIALS = True
    OAUTH2_PROVIDERS = {
        # https://developers.google.com/identity/protocols/oauth2/web-server
        # #httprest
        'google': {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
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
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'authorize_url': 'https://github.com/login/oauth/authorize',
            'access_token_url': 'https://github.com/login/oauth/access_token',
            'get_user': {
                'url': 'https://api.github.com/user/emails',
                'email': lambda json: json[0]['email'],
            },
            'scopes': ['user:email'],
        },
    }
    OAUTH2_REDIRECT_URI = settings.OAUTH2_REDIRECT_URI or \
        'http://localhost:3000/oauth2/{provider}/callback'

    # API documentation
    APIFAIRY_TITLE = 'Microblog API'
    APIFAIRY_VERSION = '1.0'
    APIFAIRY_UI = settings.DOCS_UI or 'elements'
    APIFAIRY_TAGS = ['tokens', 'users', 'posts']

    # email options
    MAIL_SERVER = settings.MAIL_SERVER or 'localhost'
    MAIL_PORT = int(settings.MAIL_PORT or '25')
    MAIL_USE_TLS = as_bool(settings.MAIL_USE_TLS)
    MAIL_USERNAME = settings.MAIL_USERNAME
    MAIL_PASSWORD = settings.MAIL_PASSWORD
    MAIL_DEFAULT_SENDER = settings.MAIL_DEFAULT_SENDER or \
        'donotreply@microblog.example.com'
