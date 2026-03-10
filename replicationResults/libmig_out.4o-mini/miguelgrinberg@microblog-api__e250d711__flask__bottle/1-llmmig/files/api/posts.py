from bottle import abort, response
from apifairy import authenticate, body

from api import db
from api.models import User, Post
from api.schemas import PostSchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.schemas import DateTimePaginationSchema

post_schema = PostSchema()
posts_schema = PostSchema(many=True)
update_post_schema = PostSchema(partial=True)

@route('/posts', methods=['POST'])
@authenticate(token_auth)
@body(post_schema)
def new(args):
    """Create a new post"""
    user = token_auth.current_user()
    post = Post(author=user, **args)
    db.session.add(post)
    db.session.commit()
    return post

@route('/posts/<id:int>', methods=['GET'])
@authenticate(token_auth)
def get(id):
    """Retrieve a post by id"""
    post = db.session.get(Post, id)
    if post is None:
        abort(404)
    return post

@route('/posts', methods=['GET'])
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve all posts"""
    return Post.select()

@route('/users/<id:int>/posts', methods=['GET'])
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def user_all(id):
    """Retrieve all posts from a user"""
    user = db.session.get(User, id)
    if user is None:
        abort(404)
    return user.posts.select()

@route('/posts/<id:int>', methods=['PUT'])
@authenticate(token_auth)
@body(update_post_schema)
def put(data, id):
    """Edit a post"""
    post = db.session.get(Post, id)
    if post is None:
        abort(404)
    if post.author != token_auth.current_user():
        abort(403)
    post.update(data)
    db.session.commit()
    return post

@route('/posts/<id:int>', methods=['DELETE'])
@authenticate(token_auth)
def delete(id):
    """Delete a post"""
    post = db.session.get(Post, id)
    if post is None:
        abort(404)
    if post.author != token_auth.current_user():
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return '', 204

@route('/feed', methods=['GET'])
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def feed():
    """Retrieve the user's post feed"""
    user = token_auth.current_user()
    return user.followed_posts_select()
