from flask import Blueprint

from ..models import Permission, Role
from . import errors, views

main = Blueprint("main", __name__)



@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
