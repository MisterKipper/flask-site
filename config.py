import os

import dotenv

try:
    dotenv.load_dotenv(dotenv.find_dotenv())
except Exception as e:
    print(f"Couldn't load .env: {e.message}")

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 0.5
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT"))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SUBJECT_PREFIX = "[Kyle's junk] "
    MAIL_SENDER = os.environ.get("MAIL_SENDER")
    ADMIN_ADDRESS = os.environ.get("ADMIN_ADDRESS")
    POSTS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    SQLALCHEMY_DATABASE_URI = (os.environ.get("DEV_DATABASE_URL") or
                               "sqlite:///" + os.path.join(basedir, "dev.sqlite"))


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (os.environ.get("TEST_DATABASE_URL") or "sqlite://")
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = (os.environ.get("DATABASE_URL") or
                               "sqlite:///" + os.path.join(basedir, "prod.sqlite"))


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
