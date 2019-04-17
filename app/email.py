from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    if not isinstance(to, list):
        to = [to]
    app = current_app._get_current_object()
    msg = Message(
        app.config["MAIL_SUBJECT_PREFIX"] + subject,
        sender=app.config["MAIL_SENDER"],
        recipients=to)
    msg.body = render_template(template + ".txt.j2", **kwargs)
    msg.html = render_template(template + ".html.j2", **kwargs)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread
