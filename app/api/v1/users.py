from flask import jsonify

from . import api
from ...models import Post, User


@api.route("/users/<int:id>")
def get_user(id):
    user = User.get_or_404(id)
    return jsonify(user.to_dict())


@api.route("/users/<int:id>/posts/")
def get_user_posts(id):
    user = User.get_or_404(id)
    posts = Post.query.with_parent(user).all()
    return jsonify({"user": user.to_dict(), "posts": [post.to_dict() for post in posts]})
