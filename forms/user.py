from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
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
