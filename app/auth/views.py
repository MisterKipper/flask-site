from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from .. import db
from ..email import send_email
from ..models import User
from . import auth
from .forms import LoginForm, RegistrationForm


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/login.html.j2", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=form.password.data,
                    email=form.email.data,
                    active=False)
        db.session.add(user)
        db.session.commit()
        flash("You have registered for my site. "
              "Please check your email for instructions on activating your account.")
        token = user.generate_activation_token()
        send_email(user.email, "Account activation", "auth/email/activate", user=user, token=token)
        return redirect(url_for("main.index"))
    return render_template("auth/register.html.j2", form=form)


@auth.route("/activate/<token>")
@login_required
def activate(token):
    if current_user.active:
        return redirect(url_for("main.index"))
    if current_user.activate(token):
        db.session.commit()
        flash("Account activated.")
    else:
        flash("Activation link invalid.")
    return redirect(url_for("main.index"))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.seen()
        if (not current_user.active and request.blueprint != "auth" and
                request.endpoint != "static"):
            return redirect(url_for("auth.inactive"))


@auth.route("/inactive-account")
def inactive():
    if current_user.is_anonymous or current_user.active:
        return redirect(url_for("main.index"))
    return render_template("auth/inactive.html.j2")


@auth.route("/activate")
@login_required
def resend_activation():
    token = current_user.generate_activation_token()
    send_email(current_user.email,
               "Account activation",
               "auth/email/activate",
               user=current_user,
               token=token)
    flash("A new activation link has been sent to you by email")
    return redirect(url_for("main.index"))
