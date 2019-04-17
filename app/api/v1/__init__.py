from flask import Blueprint

from . import authentication, comments, errors, posts, users

api = Blueprint("api", __name__)
