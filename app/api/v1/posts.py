from flask import g, jsonify, request, url_for

from ... import db
from ...models import Permission, Post
from . import api
from .authentication import forbidden
from .decorators import admin_required, permission_required


@api.route("/posts/")
def get_posts():
    posts = Post.query.all()
    return jsonify({"posts": [post.to_dict() for post in posts]})


@api.route("/posts/", methods=["POST"])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201, {"Location": url_for("api.get_post", id=post.id)}


@api.route("/posts/<int:id>")
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_dict())


@api.route("/posts/<int:id>", methods=["PUT"])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMIN):
        return forbidden("Insufficient permissions")
    post.body = request.json.get("body", post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict())


@api.route("/posts/<int:id>", methods=["DELETE"])
@admin_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return (jsonify({"posts_url": url_for("api.get_posts")}), 200)
