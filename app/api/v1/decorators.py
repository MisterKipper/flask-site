from functools import wraps

from flask import g

from ...models import Permission
from .authentication import forbidden


def permission_required(permission):
    def decorator(route_handler):
        @wraps(route_handler)
        def check_permission_and_handle(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden("Insufficient permissions")
            return route_handler(*args, **kwargs)

        return check_permission_and_handle

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
