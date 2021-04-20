from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import PasswordField, StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from api.models.users import User


class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=User.min_username_length,
                                                                          max=User.max_username_length)],
                           description=f"Length must be between {User.min_username_length} "
                                       f"and {User.max_username_length}")
    password = PasswordField("Password", validators=[DataRequired()])
    password_again = PasswordField("Repeat password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign up")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class UserProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=User.min_username_length,
                                                                          max=User.max_username_length)],
                           description=f"Length must be between {User.min_username_length} "
                                       f"and {User.max_username_length}")
    avatar = FileField("Avatar", validators=[FileAllowed(["png", "jpg", "jpeg"])])
    bio = TextAreaField("Bio", validators=[Length(max=User.max_bio_length)],
                        description=f"Length cannot be longer than {User.max_bio_length}")
    submit = SubmitField("Update")


class UserEmailForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Update")


class UserChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired()])
    new_password = PasswordField("New password", validators=[DataRequired()])
    new_password_again = PasswordField("Repeat new password", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Update")


class UserChangeGroupForm(FlaskForm):
    group = SelectField("Group", coerce=int, choices=[])
    submit = SubmitField("Update")


class UserChangePointsForm(FlaskForm):
    action = SelectField("Action", coerce=int, choices=[(-1, "Remove"), (1, "Add")])
    count = IntegerField("Count")
    submit = SubmitField("Update")
