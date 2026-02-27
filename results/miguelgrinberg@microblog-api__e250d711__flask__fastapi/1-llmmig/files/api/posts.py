from fastapi import APIRouter, Depends, HTTPException, status
from apifairy import body, response, other_responses

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


@router.post('/posts', status_code=201)
@response(post_schema)
def new(args: dict = body(post_schema), user=Depends(token_auth.current_user)):
    """Create a new post"""
    post = Post(author=user, **args)
    db.session.add(post)
    db.session.commit()
    return post


@router.get('/posts/{id}')
@response(post_schema)
@other_responses({404: 'Post not found'})
def get(id: int, user=Depends(token_auth.current_user)):
    """Retrieve a post by id"""
    post = db.session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get('/posts')
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def all(user=Depends(token_auth.current_user)):
    """Retrieve all posts"""
    return Post.select()


@router.get('/users/{id}/posts')
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
@other_responses({404: 'User not found'})
def user_all(id: int, user=Depends(token_auth.current_user)):
    """Retrieve all posts from a user"""
    user = db.session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.posts.select()


@router.put('/posts/{id}')
@response(post_schema)
@other_responses({403: 'Not allowed to edit this post',
                  404: 'Post not found'})
def put(data: dict = body(update_post_schema), id: int = None, user=Depends(token_auth.current_user)):
    """Edit a post"""
    post = db.session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author != user:
        raise HTTPException(status_code=403, detail="Not allowed to edit this post")
    post.update(data)
    db.session.commit()
    return post


@router.delete('/posts/{id}', status_code=204)
@other_responses({403: 'Not allowed to delete the post'})
def delete(id: int, user=Depends(token_auth.current_user)):
    """Delete a post"""
    post = db.session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author != user:
        raise HTTPException(status_code=403, detail="Not allowed to delete this post")
    db.session.delete(post)
    db.session.commit()
    return '', 204


@router.get('/feed')
@paginated_response(posts_schema, order_by=Post.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def feed(user=Depends(token_auth.current_user)):
    """Retrieve the user's post feed"""
    return user.followed_posts_select()
