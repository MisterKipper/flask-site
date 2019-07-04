from flask import (abort, current_app, flash, redirect, render_template, request, url_for)
from flask_login import current_user, login_required
from flask_sqlalchemy import get_debug_queries

from .. import db
from ..decorators import admin_required, permission_required
from ..models import Comment, Permission, Post, Role, User
from . import main
from .forms import CommentForm, EditProfileAdminForm, EditProfileForm, PostForm


@main.route("/", methods=["GET", "POST"])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)
    posts = pagination.items
    return render_template("index.html.j2", posts=posts, form=form, pagination=pagination)


@main.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template("user.html.j2", user=user, posts=posts)


@main.route("/post/<slug>", methods=["GET", "POST"])
def post(slug):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        comment = Comment(author=current_user._get_current_object(), post=post, body=form.body.data)
        db.session.add(comment)
        db.session.commit()
        flash("Comment added.")
        return redirect(url_for(".post", id=post.id, page=-1))
    comments = post.comments.filter_by(parent=None).order_by(Comment.timestamp.desc())
    return render_template("post.html.j2", post=post, form=form, comments=comments)


@main.route("/post/edit/<slug>", methods=["GET", "POST"])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    if not (current_user.is_admin() or current_user == post.author):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash("Post updated.")
        return redirect(url_for(".post", id=post.id))
    form.body.data = post.body
    return render_template("edit-post.html.j2", form=form)


@main.route("/comment/edit/<int:id>", methods=["GET", "POST"])
def edit_comment(id):
    comment = Comment.query.get_or_404(id)
    if not (current_user.can(Permission.MODERATE) or current_user == comment.author):
        abort(403)
    form = CommentForm()
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
        flash("Comment edited.")
        return redirect(url_for(".post", id=comment.post_id))
    form.body.data = comment.body
    return render_template("edit-comment.html.j2", form=form, comment=comment)


@main.route("/comment/reply/<int:id>", methods=["GET", "POST"])
@login_required
def reply_to_comment(id):
    parent = Comment.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(author=current_user._get_current_object(),
                          post=parent.post,
                          body=form.body.data,
                          parent_id=id)
        db.session.add(comment)
        db.session.commit()
        flash("Comment created.")
        return redirect(url_for(".post", id=comment.post_id))
    return render_template("comment.html.j2", form=form, comments=[parent])


@main.route("/admin")
@login_required
@admin_required
def for_admins_only():
    return "My admin page."


@main.route("/moderate")
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get("page", 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config["COMMENTS_PER_PAGE"], error_out=False)
    comments = pagination.items
    return render_template("moderate.html.j2", comments=comments, pagination=pagination, page=page)


@main.route("/moderate/enable/<int:id>")
@login_required
@permission_required(Permission.MODERATE)
def enable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get("page", 1, type=int)))


@main.route("/moderate/disable/<int:id>")
@login_required
@permission_required(Permission.MODERATE)
def disable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get("page", 1, type=int)))


@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("Your profile has been updated.")
        return redirect(url_for(".user"), username=current_user.username)
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit-profile.html.j2", form=form)


@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.active = form.active.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("The profile has been updated.")
        return redirect(url_for(".user", username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.active.data = user.active
    form.role.data = user.role
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template("edit-profile.html.j2", form=form, user=user)


@main.route("/shutdown")
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get("werkzeug.server.shutdown")
    if not shutdown:
        abort(500)
    shutdown()
    return "Shutting down..."


@main.route("/demos")
def demos():
    return render_template("demos.html.j2")


@main.route("/about-me")
def about_me():
    return render_template("about-me.html.j2")


@main.route("/blog")
def blog():
    return render_template("blog.html.j2")


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config["DB_SLOW_QUERY_TIME"]:
            current_app.logger.warning(f"Slow query: {query.statement}\n"
                                       f"Parameters: {query.parameters}\n"
                                       f"Duration: {query.duration}\n"
                                       f"Context: {query.context}")
    return response
