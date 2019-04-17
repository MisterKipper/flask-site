from flask import g

from ...models import Permission


def to_dict_safe(comment):
    comment = comment.to_dict()
    if comment.disabled and not g.current_user.can(Permission.MODERATE):
        comment.body = "Comment disabled."
        comment.body_html = "<p><i>Comment disabled.</i></p>"
    return comment
