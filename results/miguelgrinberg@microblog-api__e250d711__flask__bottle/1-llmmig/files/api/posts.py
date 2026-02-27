from bottle import Bottle, abort, request
from apifairy import authenticate, body, response, other_responses

from api import db
from api.models import User, Post
from api.schemas import PostSchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.schemas import DateTimePaginationSchema

app = Bottle()
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
update_post_schema = PostSchema(partial=True)


@app.route('/posts', method='POST')
@authenticate(token_auth)
@body(post_schema)
def new(args):
    """Create a new post"""
    user = token_auth.current_user()
    post = Post(author=user, **args)
    db.session.add(post)
    db.session.commit()
    return post_schema.dump(post), 201


@app.route('/posts/<id:int>', method='GET')
@authenticate(token_auth)
def get(id):
    """Retrieve a post by id"""
    post = db.session.get(Post, id) or abort(404, "Post not found")
    return post_schema.dump(post)


@app.route('/posts', method='GET')
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve all posts"""
    return Post.select()


@app.route('/users/<id:int>/posts', method='GET')
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def user_all(id):
    """Retrieve all posts from a user"""
    user = db.session.get(User, id) or abort(404, "User not found")
    return user.posts.select()


@app.route('/posts/<id:int>', method='PUT')
@authenticate(token_auth)
@body(update_post_schema)
def put(data, id):
    """Edit a post"""
    post = db.session.get(Post, id) or abort(404, "Post not found")
    if post.author != token_auth.current_user():
        abort(403, "Not allowed to edit this post")
    post.update(data)
    db.session.commit()
    return post_schema.dump(post)


@app.route('/posts/<id:int>', method='DELETE')
@authenticate(token_auth)
def delete(id):
    """Delete a post"""
    post = db.session.get(Post, id) or abort(404, "Post not found")
    if post.author != token_auth.current_user():
        abort(403, "Not allowed to delete the post")
    db.session.delete(post)
    db.session.commit()
    return '', 204


@app.route('/feed', method='GET')
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def feed():
    """Retrieve the user's post feed"""
    user = token_auth.current_user()
    return user.followed_posts_select()
