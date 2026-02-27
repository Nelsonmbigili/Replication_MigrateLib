### Explanation of Changes

To migrate the code from Flask to FastAPI, the following changes were made:

1. **`current_app` Replacement**: In Flask, `current_app` is used to access the application context and configuration. In FastAPI, this is replaced by directly passing the configuration as a dependency or using a global configuration object.
2. **`url_for` Replacement**: Flask's `url_for` is replaced with FastAPI's `url_for` from `fastapi.routing`.
3. **JWT Handling**: The `jwt` library usage remains unchanged as it is independent of the web framework.
4. **Database Session**: The database session handling (`db.session`) remains unchanged as it is not tied to Flask.
5. **No Flask-Specific Imports**: Removed Flask-specific imports (`from flask import current_app, url_for`) and replaced them with FastAPI-compatible alternatives.

Below is the modified code:

---

### Modified Code
```python
from datetime import datetime, timedelta
from hashlib import md5
import secrets
from time import time
from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.routing import APIRouter
import jwt
from alchemical import Model
import sqlalchemy as sa
from sqlalchemy import orm as so
from werkzeug.security import generate_password_hash, check_password_hash

from api.app import db, app_config  # Assuming app_config is a global configuration object
from api.dates import naive_utcnow


class Updateable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)


followers = sa.Table(
    'followers',
    Model.metadata,
    sa.Column('follower_id', sa.ForeignKey('users.id'), primary_key=True),
    sa.Column('followed_id', sa.ForeignKey('users.id'), primary_key=True)
)


class Token(Model):
    __tablename__ = 'tokens'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    access_token: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    access_expiration: so.Mapped[datetime]
    refresh_token: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    refresh_expiration: so.Mapped[datetime]
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('users.id'), index=True)

    user: so.Mapped['User'] = so.relationship(back_populates='tokens')

    @property
    def access_token_jwt(self):
        return jwt.encode({'token': self.access_token},
                          app_config['SECRET_KEY'],  # Use global app_config
                          algorithm='HS256')

    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = naive_utcnow() + \
            timedelta(minutes=app_config['ACCESS_TOKEN_MINUTES'])
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = naive_utcnow() + \
            timedelta(days=app_config['REFRESH_TOKEN_DAYS'])

    def expire(self, delay=None):
        if delay is None:  # pragma: no branch
            # 5 second delay to allow simultaneous requests
            delay = 5 if not app_config.get('TESTING', False) else 0
        self.access_expiration = naive_utcnow() + timedelta(seconds=delay)
        self.refresh_expiration = naive_utcnow() + timedelta(seconds=delay)

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = naive_utcnow() - timedelta(days=1)
        db.session.execute(Token.delete().where(
            Token.refresh_expiration < yesterday))

    @staticmethod
    def from_jwt(access_token_jwt):
        access_token = None
        try:
            access_token = jwt.decode(access_token_jwt,
                                      app_config['SECRET_KEY'],  # Use global app_config
                                      algorithms=['HS256'])['token']
            return db.session.scalar(Token.select().filter_by(
                access_token=access_token))
        except jwt.PyJWTError:
            pass


class User(Updateable, Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    first_seen: so.Mapped[datetime] = so.mapped_column(default=naive_utcnow)
    last_seen: so.Mapped[datetime] = so.mapped_column(default=naive_utcnow)

    tokens: so.WriteOnlyMapped['Token'] = so.relationship(
        back_populates='user')
    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')

    def followed_posts_select(self):
        Author = so.aliased(User)
        return Post.select().join(Post.author.of_type(Author)).join(
            Author.followers, isouter=True).group_by(Post).where(
                sa.or_(Post.author == self, User.id == self.id))

    def __repr__(self):  # pragma: no cover
        return '<User {}>'.format(self.username)

    @property
    def url(self):
        return f"/users/{self.id}"  # Replace Flask's url_for with a direct URL

    @property
    def has_password(self):
        return self.password_hash is not None

    @property
    def avatar_url(self):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash:  # pragma: no branch
            return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = naive_utcnow()

    def generate_auth_token(self):
        token = Token(user=self)
        token.generate()
        return token

    @staticmethod
    def verify_access_token(access_token_jwt, refresh_token=None):
        token = Token.from_jwt(access_token_jwt)
        if token:
            if token.access_expiration > naive_utcnow():
                token.user.ping()
                db.session.commit()
                return token.user

    @staticmethod
    def verify_refresh_token(refresh_token, access_token_jwt):
        token = Token.from_jwt(access_token_jwt)
        if token and token.refresh_token == refresh_token:
            if token.refresh_expiration > naive_utcnow():
                return token

            # someone tried to refresh with an expired token
            # revoke all tokens from this user as a precaution
            token.user.revoke_all()
            db.session.commit()

    def revoke_all(self):
        db.session.execute(Token.delete().where(Token.user == self))

    def generate_reset_token(self):
        return jwt.encode(
            {
                'exp': time() + app_config['RESET_TOKEN_MINUTES'] * 60,
                'reset_email': self.email,
            },
            app_config['SECRET_KEY'],  # Use global app_config
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(reset_token):
        try:
            data = jwt.decode(reset_token, app_config['SECRET_KEY'],
                              algorithms=['HS256'])
        except jwt.PyJWTError:
            return
        return db.session.scalar(User.select().filter_by(
            email=data['reset_email']))

    def follow(self, user):
        if not self.is_following(user):
            db.session.execute(followers.insert().values(
                follower_id=self.id, followed_id=user.id))

    def unfollow(self, user):
        if self.is_following(user):
            db.session.execute(followers.delete().where(
                followers.c.follower_id == self.id,
                followers.c.followed_id == user.id))

    def is_following(self, user):
        return db.session.scalars(User.select().where(
            User.id == self.id, User.following.contains(
                user))).one_or_none() is not None


class Post(Updateable, Model):
    __tablename__ = 'posts'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    text: so.Mapped[str] = so.mapped_column(sa.String(280))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=naive_utcnow)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True)

    author: so.Mapped['User'] = so.relationship(back_populates='posts')

    def __repr__(self):  # pragma: no cover
        return '<Post {}>'.format(self.text)

    @property
    def url(self):
        return f"/posts/{self.id}"  # Replace Flask's url_for with a direct URL
```

---

### Key Notes:
- `app_config` is assumed to be a global configuration object in the FastAPI application, replacing `current_app.config`.
- `url_for` is replaced with direct URL strings since FastAPI does not have a direct equivalent for `url_for` in this context.
- The database session (`db.session`) and JWT handling remain unchanged as they are not tied to Flask.