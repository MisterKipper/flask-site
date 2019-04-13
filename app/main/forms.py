import wtforms
import wtforms.validators as validators
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField
from flask_pagedown.fields import PageDownField

from ..models import User, Role


class EditProfileForm(FlaskForm):
    name = StringField("Real name", validators=[validators.Length(0, 64)])
    location = StringField("Location", validators=[validators.Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField("Submit")


class EditProfileAdminForm(EditProfileForm):
    email = StringField(
        "Email",
        validators=[validators.DataRequired(),
                    validators.Length(1, 254),
                    validators.Email()])
    username = StringField(
        "Username",
        validators=[
            validators.DataRequired(),
            validators.Length(1, 64),
            validators.Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$", 0,
                "Username must consist only of lettters, numbers, underscores, and dots.")
        ])
    active = BooleanField("Activated")
    role = SelectField("Role", coerce=int)
    submit = SubmitField("Submit")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise wtforms.ValidationError("Email already registered.")

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise wtforms.ValidationError("Username already in use.")


class PostForm(FlaskForm):
    body = PageDownField("Post text goes here.", validators=[validators.DataRequired()])
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    body = PageDownField("", validators=[validators.DataRequired()])
    submit = SubmitField("Submit")
