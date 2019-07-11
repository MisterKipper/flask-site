from wtforms import HiddenField


def is_hidden_field(field):
    return isinstance(field, HiddenField)


def jinja_init(app):
    app.jinja_env.globals["is_hidden_field"] = is_hidden_field
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True
