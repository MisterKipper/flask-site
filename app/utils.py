from random import randint
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from flask import current_app
from faker import Faker

from . import db
from .models import User, Post


def insert_admin():
    u = User(
        email=current_app.config["ADMIN_ADDRESS"],
        username="kyle",
        password=current_app.config["ADMIN_PASSWORD"],
        active=True,
        member_since=datetime.utcnow())
    db.session.add(u)
    db.session.commit()


def insert_fake_users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(
            email=fake.email(),
            username=fake.user_name(),
            password="password",
            active=True,
            name=fake.name(),
            location=fake.city(),
            about_me=fake.text(),
            member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def insert_fake_posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(), timestamp=fake.past_date(), author=u)
        db.session.add(p)
    db.session.commit()
