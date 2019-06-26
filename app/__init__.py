from flask import Flask
# from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy

from config import config
from .jinja_utils import jinja_init

db = SQLAlchemy()
login = LoginManager()
login.login_view = "auth.login"
# bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
pagedown = PageDown()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    jinja_init(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login.init_app(app)
    pagedown.init_app(app)
    if app.config["SSL_REDIRECT"]:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return app
