import os
import sys
import click

from flask_migrate import Migrate, upgrade

import app.utils as utils
from app import create_app, db
from app.models import Comment, Post, Role, User

COV = None
if os.environ.get("FLASK_COVERAGE"):
    import coverage
    COV = coverage.coverage(branch=True, include="app/*")
    COV.start()

app = create_app(os.getenv("FLASK_ENV") or "default")
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Post": Post, "Role": Role, "Comment": Comment}


@app.cli.command()
@click.option("--coverage/--no-coverage", default=False, help="Run tests under code coverage.")
def test(coverage):
    if coverage and not os.environ.get("FLASK_COVERAGE"):
        os.environ["FLASK_COVERAGE"] = "1"
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print("Coverage summary:")
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, "tmp", "coverage")
        COV.html_report(directory=covdir)
        print(f"HTML version: file://{covdir}/index.html")
        COV.erase()


@app.cli.command()
@click.option("--length", default=25, help="Number of functions to include in the profiler report.")
@click.option("--profile-dir", default=None, help="Directory where profiler data files are saved.")
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run(debug=False)


@app.cli.command()
def deploy():
    upgrade()
    Role.insert_roles()


@app.cli.command()
def dev_setup():
    upgrade()
    Role.insert_roles()
    if not User.query.count() > 0:
        utils.insert_admin()
        utils.insert_fake_users()
    utils.insert_fake_posts()
    utils.insert_fake_comments()
