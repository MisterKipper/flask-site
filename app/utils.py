import os
from datetime import datetime
from random import randint

from flask import current_app
from sqlalchemy.exc import IntegrityError

from . import db
from .models import Comment, Post, Role, User


def insert_admin():
    if not User.query.filter_by(username=os.environ["ADMIN_USERNAME"]).first():
        u = User(email=os.environ["ADMIN_ADDRESS"],
                 username="kyle",
                 password=os.environ["ADMIN_PASSWORD"],
                 active=True,
                 member_since=datetime.utcnow())
        db.session.add(u)
        db.session.commit()


def insert_fake_users(count=100):
    from faker import Faker
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password="password",
                 active=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_datetime())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def insert_fake_posts(count=100):
    from faker import Faker
    fake = Faker()
    admin = Role.query.filter_by(name="admin").first()
    u = User.query.filter_by(role=admin).first()
    for i in range(count):
        body = fake.text(max_nb_chars=1000)
        p = Post(title=fake.text(max_nb_chars=80),
                 body=body,
                 summary=body[:200],
                 timestamp=fake.past_datetime(),
                 author=u)
        db.session.add(p)
    db.session.commit()


def insert_fake_comments(count=1000):
    from faker import Faker
    fake = Faker()
    post_count = Post.query.count()
    user_count = User.query.count()
    for i in range(count):
        user = User.query.offset(randint(0, user_count - 1)).first()
        post = Post.query.offset(randint(0, post_count - 1)).first()
        comment_count = Comment.query.filter_by(post=post).count()
        if comment_count and randint(0, 1):
            parent = Comment.query.filter_by(post=post)\
                                  .offset(randint(0, comment_count - 1))\
                                  .first()
            timestamp = fake.date_time_between(parent.timestamp, "now")
        else:
            parent = None
            timestamp = fake.date_time_between(post.timestamp, "now")
        c = Comment(body=fake.text(), timestamp=timestamp, author=user, post=post, parent=parent)
        db.session.add(c)
    db.session.commit()
