from tornado.web import Application, RequestHandler
from tornado.escape import json_decode, json_encode
from api import db
from api.models import User, Post
from api.schemas import PostSchema
from api.auth import token_auth
from api.decorators import paginated_response
from api.schemas import DateTimePaginationSchema

post_schema = PostSchema()
posts_schema = PostSchema(many=True)
update_post_schema = PostSchema(partial=True)


class BaseHandler(RequestHandler):
    def prepare(self):
        """Authenticate user for all requests."""
        token_auth.authenticate(self.request)

    def write_error(self, status_code, **kwargs):
        """Handle errors."""
        self.set_status(status_code)
        self.finish({"error": kwargs.get("message", "An error occurred")})


class NewPostHandler(BaseHandler):
    def post(self):
        """Create a new post"""
        args = json_decode(self.request.body)
        errors = post_schema.validate(args)
        if errors:
            self.set_status(400)
            self.finish({"errors": errors})
            return

        user = token_auth.current_user()
        post = Post(author=user, **args)
        db.session.add(post)
        db.session.commit()
        self.set_status(201)
        self.write(post_schema.dump(post))


class GetPostHandler(BaseHandler):
    def get(self, id):
        """Retrieve a post by id"""
        post = db.session.get(Post, id)
        if not post:
            self.set_status(404)
            self.finish({"error": "Post not found"})
            return
        self.write(post_schema.dump(post))


class AllPostsHandler(BaseHandler):
    def get(self):
        """Retrieve all posts"""
        posts = Post.select()
        paginated_data = paginated_response(posts, posts_schema, order_by=Post.timestamp,
                                            order_direction='desc',
                                            pagination_schema=DateTimePaginationSchema)
        self.write(json_encode(paginated_data))


class UserPostsHandler(BaseHandler):
    def get(self, id):
        """Retrieve all posts from a user"""
        user = db.session.get(User, id)
        if not user:
            self.set_status(404)
            self.finish({"error": "User not found"})
            return
        posts = user.posts.select()
        paginated_data = paginated_response(posts, posts_schema, order_by=Post.timestamp,
                                            order_direction='desc',
                                            pagination_schema=DateTimePaginationSchema)
        self.write(json_encode(paginated_data))


class EditPostHandler(BaseHandler):
    def put(self, id):
        """Edit a post"""
        post = db.session.get(Post, id)
        if not post:
            self.set_status(404)
            self.finish({"error": "Post not found"})
            return

        if post.author != token_auth.current_user():
            self.set_status(403)
            self.finish({"error": "Not allowed to edit this post"})
            return

        data = json_decode(self.request.body)
        errors = update_post_schema.validate(data)
        if errors:
            self.set_status(400)
            self.finish({"errors": errors})
            return

        post.update(data)
        db.session.commit()
        self.write(post_schema.dump(post))


class DeletePostHandler(BaseHandler):
    def delete(self, id):
        """Delete a post"""
        post = db.session.get(Post, id)
        if not post:
            self.set_status(404)
            self.finish({"error": "Post not found"})
            return

        if post.author != token_auth.current_user():
            self.set_status(403)
            self.finish({"error": "Not allowed to delete the post"})
            return

        db.session.delete(post)
        db.session.commit()
        self.set_status(204)
        self.finish()


class FeedHandler(BaseHandler):
    def get(self):
        """Retrieve the user's post feed"""
        user = token_auth.current_user()
        posts = user.followed_posts_select()
        paginated_data = paginated_response(posts, posts_schema, order_by=Post.timestamp,
                                            order_direction='desc',
                                            pagination_schema=DateTimePaginationSchema)
        self.write(json_encode(paginated_data))


def make_app():
    return Application([
        (r"/posts", NewPostHandler),
        (r"/posts/([0-9]+)", GetPostHandler),
        (r"/posts", AllPostsHandler),
        (r"/users/([0-9]+)/posts", UserPostsHandler),
        (r"/posts/([0-9]+)", EditPostHandler),
        (r"/posts/([0-9]+)", DeletePostHandler),
        (r"/feed", FeedHandler),
    ])
