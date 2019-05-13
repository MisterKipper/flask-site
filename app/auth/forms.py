import wtforms.validators as validators
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField

from ..models import User


class LoginForm(FlaskForm):
    username = StringField("Username",
                           validators=[validators.DataRequired(),
                                       validators.Length(1, 64)])
    password = PasswordField("Password", validators=[validators.DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Log in")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            validators.DataRequired(),
            validators.Length(1, 64, "Username maximum length is 64 characters."),
            validators.Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$", 0,
                "Username must consist only of lettters, numbers, underscores, and dots.")
        ])
    email = StringField(
        "Email address",
        validators=[validators.DataRequired(),
                    validators.Email("Invalid email address.")])
    password = PasswordField("Password", validators=[validators.DataRequired()])
    password2 = PasswordField(
        "Re-enter password", validators=[validators.DataRequired(),
                                         validators.EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise validators.ValidationError("Username already in use.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise validators.ValidationError("Email address already in use.")
