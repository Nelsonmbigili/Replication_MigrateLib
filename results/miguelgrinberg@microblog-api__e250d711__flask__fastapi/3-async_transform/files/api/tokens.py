import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Request, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import requests

from api.app import db, app
from api.auth import basic_auth, token_auth
from api.email import send_email
from api.models import User, Token
from api.schemas import TokenSchema, PasswordResetRequestSchema, \
    PasswordResetSchema, OAuth2Schema, EmptySchema

router = APIRouter()
token_schema = TokenSchema()
oauth2_schema = OAuth2Schema()


def token_response(token, response: Response):
    if app.state.config['REFRESH_TOKEN_IN_COOKIE']:
        samesite = 'strict'
        if app.state.config['USE_CORS']:  # pragma: no branch
            samesite = 'none' if not app.debug else 'lax'
        response.set_cookie(
            key='refresh_token',
            value=token.refresh_token,
            path='/tokens',
            secure=not app.debug,
            httponly=True,
            samesite=samesite
        )
    return {
        'access_token': token.access_token_jwt,
        'refresh_token': token.refresh_token
        if app.state.config['REFRESH_TOKEN_IN_BODY'] else None,
    }


@router.post('/tokens', response_model=TokenSchema, status_code=200)
async def new(response: Response, user: User = Depends(basic_auth)):
    """Create new access and refresh tokens"""
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()  # keep token table clean of old tokens
    db.session.commit()
    return token_response(token, response)


@router.put('/tokens', response_model=TokenSchema, status_code=200)
async def refresh(args: TokenSchema, request: Request, response: Response):
    """Refresh an access token"""
    access_token_jwt = args.access_token
    refresh_token = args.refresh_token or request.cookies.get('refresh_token')
    if not access_token_jwt or not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token = User.verify_refresh_token(refresh_token, access_token_jwt)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token.expire()
    new_token = token.user.generate_auth_token()
    db.session.add_all([token, new_token])
    db.session.commit()
    return token_response(new_token, response)


@router.delete('/tokens', status_code=204)
async def revoke(request: Request, user: User = Depends(token_auth)):
    """Revoke an access token"""
    access_token_jwt = request.headers['Authorization'].split()[1]
    token = Token.from_jwt(access_token_jwt)
    if not token:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token.expire()
    db.session.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/tokens/reset', status_code=204)
async def reset(args: PasswordResetRequestSchema):
    """Request a password reset token"""
    user = db.session.scalar(User.select().filter_by(email=args.email))
    if user is not None:
        reset_token = user.generate_reset_token()
        reset_url = app.state.config['PASSWORD_RESET_URL'] + \
            '?token=' + reset_token
        send_email(args.email, 'Reset Your Password', 'reset',
                   username=user.username, token=reset_token, url=reset_url)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/tokens/reset', status_code=204)
async def password_reset(args: PasswordResetSchema):
    """Reset a user password"""
    user = User.verify_reset_token(args.token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    user.password = args.new_password
    db.session.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/tokens/oauth2/{provider}', status_code=302)
async def oauth2_authorize(provider: str):
    """Initiate OAuth2 authentication with a third-party provider"""
    provider_data = app.state.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    session['oauth2_state'] = secrets.token_urlsafe(16)
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': app.state.config['OAUTH2_REDIRECT_URI'].format(
            provider=provider),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })
    return RedirectResponse(url=provider_data['authorize_url'] + '?' + qs)


@router.post('/tokens/oauth2/{provider}', response_model=TokenSchema)
async def oauth2_new(args: OAuth2Schema, provider: str):
    """Create new access and refresh tokens with OAuth2 authentication"""
    provider_data = app.state.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if args.state != session.get('oauth2_state'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    response = requests.post(provider_data['access_token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': args.code,
        'grant_type': 'authorization_code',
        'redirect_uri': app.state.config['OAUTH2_REDIRECT_URI'].format(
            provider=provider),
    }, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    response = requests.get(provider_data['get_user']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    email = provider_data['get_user']['email'](response.json())
    user = db.session.scalar(User.select().where(User.email == email))
    if user is None:
        user = User(email=email, username=email.split('@')[0])
        db.session.add(user)
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()  # keep token table clean of old tokens
    db.session.commit()
    return token_response(token, Response())
