from dynaconf import settings
import os

basedir = os.path.abspath(os.path.dirname(__file__))


def as_bool(value):
    if value:
        return value.lower() in ['true', 'yes', 'on', '1']
    return False


class Config:
    # database options
    ALCHEMICAL_DATABASE_URL = settings.get('DATABASE_URL', 
                                           f'sqlite:///{os.path.join(basedir, "db.sqlite")}')
    ALCHEMICAL_ENGINE_OPTIONS = {'echo': as_bool(settings.get('SQL_ECHO', 'false'))}

    # security options
    SECRET_KEY = settings.get('SECRET_KEY', 'top-secret!')
    DISABLE_AUTH = as_bool(settings.get('DISABLE_AUTH', 'false'))
    ACCESS_TOKEN_MINUTES = settings.get('ACCESS_TOKEN_MINUTES', 15)
    REFRESH_TOKEN_DAYS = settings.get('REFRESH_TOKEN_DAYS', 7)
    REFRESH_TOKEN_IN_COOKIE = as_bool(settings.get('REFRESH_TOKEN_IN_COOKIE', 'yes'))
    REFRESH_TOKEN_IN_BODY = as_bool(settings.get('REFRESH_TOKEN_IN_BODY', 'false'))
    RESET_TOKEN_MINUTES = settings.get('RESET_TOKEN_MINUTES', 15)
    PASSWORD_RESET_URL = settings.get('PASSWORD_RESET_URL', 'http://localhost:3000/reset')
    USE_CORS = as_bool(settings.get('USE_CORS', 'yes'))
    CORS_SUPPORTS_CREDENTIALS = True
    OAUTH2_PROVIDERS = {
        # https://developers.google.com/identity/protocols/oauth2/web-server
        # #httprest
        'google': {
            'client_id': settings.get('GOOGLE_CLIENT_ID'),
            'client_secret': settings.get('GOOGLE_CLIENT_SECRET'),
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
            'client_id': settings.get('GITHUB_CLIENT_ID'),
            'client_secret': settings.get('GITHUB_CLIENT_SECRET'),
            'authorize_url': 'https://github.com/login/oauth/authorize',
            'access_token_url': 'https://github.com/login/oauth/access_token',
            'get_user': {
                'url': 'https://api.github.com/user/emails',
                'email': lambda json: json[0]['email'],
            },
            'scopes': ['user:email'],
        },
    }
    OAUTH2_REDIRECT_URI = settings.get('OAUTH2_REDIRECT_URI', 
                                       'http://localhost:3000/oauth2/{provider}/callback')

    # API documentation
    APIFAIRY_TITLE = 'Microblog API'
    APIFAIRY_VERSION = '1.0'
    APIFAIRY_UI = settings.get('DOCS_UI', 'elements')
    APIFAIRY_TAGS = ['tokens', 'users', 'posts']

    # email options
    MAIL_SERVER = settings.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = settings.get('MAIL_PORT', 25)
    MAIL_USE_TLS = as_bool(settings.get('MAIL_USE_TLS', 'false'))
    MAIL_USERNAME = settings.get('MAIL_USERNAME')
    MAIL_PASSWORD = settings.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = settings.get('MAIL_DEFAULT_SENDER', 
                                       'donotreply@microblog.example.com')
