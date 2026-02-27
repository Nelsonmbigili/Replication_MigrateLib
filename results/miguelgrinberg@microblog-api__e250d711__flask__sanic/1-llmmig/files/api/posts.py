from sanic import Blueprint
from sanic.exceptions import SanicException
from apifairy import authenticate, body, other_responses

from api import db
from api.models import User, Post
from api.schemas import PostSchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.schemas import DateTimePaginationSchema

posts = Blueprint('posts', url_prefix='/posts')
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
update_post_schema = PostSchema(partial=True)


@posts.route('/', methods=['POST'])
@authenticate(token_auth)
@body(post_schema)
async def new(request, args):
    """Create a new post"""
    user = token_auth.current_user()
    post = Post(author=user, **args)
    db.session.add(post)
    db.session.commit()
    return post_schema.dump(post), 201


@posts.route('/<id:int>', methods=['GET'])
@authenticate(token_auth)
@other_responses({404: 'Post not found'})
async def get(request, id):
    """Retrieve a post by id"""
    post = db.session.get(Post, id)
    if not post:
        raise SanicException('Post not found', status_code=404)
    return post_schema.dump(post)


@posts.route('/', methods=['GET'])
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
async def all(request):
    """Retrieve all posts"""
    return Post.select()


@posts.route('/users/<id:int>/posts', methods=['GET'])
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
@other_responses({404: 'User not found'})
async def user_all(request, id):
    """Retrieve all posts from a user"""
    user = db.session.get(User, id)
    if not user:
        raise SanicException('User not found', status_code=404)
    return user.posts.select()


@posts.route('/<id:int>', methods=['PUT'])
@authenticate(token_auth)
@body(update_post_schema)
@other_responses({403: 'Not allowed to edit this post',
                  404: 'Post not found'})
async def put(request, data, id):
    """Edit a post"""
    post = db.session.get(Post, id)
    if not post:
        raise SanicException('Post not found', status_code=404)
    if post.author != token_auth.current_user():
        raise SanicException('Not allowed to edit this post', status_code=403)
    post.update(data)
    db.session.commit()
    return post_schema.dump(post)


@posts.route('/<id:int>', methods=['DELETE'])
@authenticate(token_auth)
@other_responses({403: 'Not allowed to delete the post'})
async def delete(request, id):
    """Delete a post"""
    post = db.session.get(Post, id)
    if not post:
        raise SanicException('Post not found', status_code=404)
    if post.author != token_auth.current_user():
        raise SanicException('Not allowed to delete the post', status_code=403)
    db.session.delete(post)
    db.session.commit()
    return '', 204


@posts.route('/feed', methods=['GET'])
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
async def feed(request):
    """Retrieve the user's post feed"""
    user = token_auth.current_user()
    return user.followed_posts_select()
