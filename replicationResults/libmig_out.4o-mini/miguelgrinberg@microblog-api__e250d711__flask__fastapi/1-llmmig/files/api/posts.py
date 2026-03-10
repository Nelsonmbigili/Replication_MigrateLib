from fastapi import APIRouter, HTTPException, Depends
from apifairy import authenticate, body, other_responses

from api import db
from api.models import User, Post
from api.schemas import PostSchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.schemas import DateTimePaginationSchema

router = APIRouter()
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
update_post_schema = PostSchema(partial=True)


@router.post('/posts', response_model=PostSchema, status_code=201)
@authenticate(token_auth)
def new(args: post_schema):
    """Create a new post"""
    user = token_auth.current_user()
    post = Post(author=user, **args)
    db.session.add(post)
    db.session.commit()
    return post


@router.get('/posts/{id}', response_model=PostSchema)
@authenticate(token_auth)
@other_responses({404: 'Post not found'})
def get(id: int):
    """Retrieve a post by id"""
    post = db.session.get(Post, id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get('/posts', response_model=List[PostSchema])
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def all():
    """Retrieve all posts"""
    return Post.select()


@router.get('/users/{id}/posts', response_model=List[PostSchema])
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
@other_responses({404: 'User not found'})
def user_all(id: int):
    """Retrieve all posts from a user"""
    user = db.session.get(User, id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user.posts.select()


@router.put('/posts/{id}', response_model=PostSchema)
@authenticate(token_auth)
def put(data: update_post_schema, id: int):
    """Edit a post"""
    post = db.session.get(Post, id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author != token_auth.current_user():
        raise HTTPException(status_code=403, detail="Not allowed to edit this post")
    post.update(data)
    db.session.commit()
    return post


@router.delete('/posts/{id}', status_code=204)
@authenticate(token_auth)
@other_responses({403: 'Not allowed to delete the post'})
def delete(id: int):
    """Delete a post"""
    post = db.session.get(Post, id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author != token_auth.current_user():
        raise HTTPException(status_code=403, detail="Not allowed to delete the post")
    db.session.delete(post)
    db.session.commit()
    return


@router.get('/feed', response_model=List[PostSchema])
@authenticate(token_auth)
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def feed():
    """Retrieve the user's post feed"""
    user = token_auth.current_user()
    return user.followed_posts_select()
