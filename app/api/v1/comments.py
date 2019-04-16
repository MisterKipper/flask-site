from flask import g, jsonify, request, url_for

from . import api
from .decorators import permission_required
from .utils import to_dict_safe
from ... import db
from ...models import Comment, Permission, Post


@api.route("/comments/")
def get_comments():
    comments = Comment.query.all()
    return jsonify([to_dict_safe(comment) for comment in comments])


@api.route("/comments/<int:id>")
def get_comment(id):
    comment = Comment.get_or_404(id)
    return jsonify(to_dict_safe(comment))


@api.route("/posts/<int:id>/comments/")
def get_post_comments(id):
    post = Post.get_or_404(id)
    comments = Comment.query.with_parent(post).all()
    return jsonify({
        "parent": post.to_dict(),
        "comments": [to_dict_safe(comment) for comment in comments]
    })


@api.route("/posts/<int:id>/comments/", methods=["POST"])
@permission_required(Permission.COMMENT)
def post_comment_on_post(id):
    post = Post.get_or_404(id)
    body = request.json.get("body")
    comment = Comment(author=g.current_user, post=post, body=body)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201, {"Location": url_for("api.get_comment", id=comment.id)}
