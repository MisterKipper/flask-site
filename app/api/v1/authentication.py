from flask import g, jsonify, request
from flask_httpauth import HTTPBasicAuth

from ...models import User
from . import api
from .errors import forbidden, unauthorized

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    print(request.authorization)
    if username_or_token == "":
        return False
    if password == "":  # No password => assume token
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=username_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized("Invalid credentials")


@api.before_request
@auth.login_required
def before_request():
    print(g.current_user)
    if not g.current_user.is_anonymous and not g.current_user.active:
        return forbidden("Unactivated account")


@api.route("/tokens/", methods=["POST"])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized("Invalid credentials")
    expiration = 3600
    return jsonify({
        "token": g.current_user.generate_auth_token(expiration),
        "expiration": expiration
    })
