from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import PasswordField, StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from qp.api.models.users import User


class RegisterForm(FlaskForm):
    email = EmailField(lazy_gettext("Email"), validators=[DataRequired(), Email()])
    username = StringField(lazy_gettext("Username"), validators=[DataRequired(), Length(min=User.min_username_length,
                                                                                        max=User.max_username_length)])
    password = PasswordField(lazy_gettext("Password"), validators=[DataRequired()])
    password_again = PasswordField(lazy_gettext("Repeat password"), validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField(lazy_gettext("Sign up"))


class LoginForm(FlaskForm):
    email = EmailField(lazy_gettext("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(lazy_gettext("Password"), validators=[DataRequired()])
    submit = SubmitField(lazy_gettext("Log in"))


class UserProfileForm(FlaskForm):
    username = StringField(lazy_gettext("Username"), validators=[DataRequired(), Length(min=User.min_username_length,
                                                                                        max=User.max_username_length)])
    avatar = FileField(lazy_gettext("Avatar"), validators=[FileAllowed(["png", "jpg", "jpeg"])])
    bio = TextAreaField(lazy_gettext("Bio"), validators=[Length(max=User.max_bio_length)])
    submit = SubmitField(lazy_gettext("Update"))


class UserEmailForm(FlaskForm):
    email = EmailField(lazy_gettext("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(lazy_gettext("Update"))


class UserChangePasswordForm(FlaskForm):
    old_password = PasswordField(lazy_gettext("Old password"), validators=[DataRequired()])
    new_password = PasswordField(lazy_gettext("New password"), validators=[DataRequired()])
    new_password_again = PasswordField(lazy_gettext("Repeat new password"),
                                       validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField(lazy_gettext("Update"))


class UserChangeGroupForm(FlaskForm):
    group = SelectField(lazy_gettext("Group"), coerce=int, choices=[])
    submit = SubmitField(lazy_gettext("Update"))


class UserChangePointsForm(FlaskForm):
    action = SelectField(lazy_gettext("Action"), coerce=int,
                         choices=[(-1, lazy_gettext("Deduct")), (1, lazy_gettext("Add"))])
    count = IntegerField(lazy_gettext("Count"))
    submit = SubmitField(lazy_gettext("Update"))
