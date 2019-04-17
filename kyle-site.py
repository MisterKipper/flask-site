import os

from flask_migrate import Migrate, upgrade

import app.utils as utils
from app import create_app, db
from app.models import User, Post, Role, Comment

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Post": Post, "Role": Role, "Comment": Comment}


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def deploy():
    upgrade()
    Role.insert_roles()


@app.cli.command()
def dev_setup():
    upgrade()
    Role.insert_roles()
    if not User.query.count() > 1:
        utils.insert_admin()
        utils.insert_fake_users()
    utils.insert_fake_posts()
    utils.insert_fake_comments()
