from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class VoteForm(FlaskForm):
    options = RadioField("Options", coerce=int, choices=[], validators=[Optional()])
    submit = SubmitField("Vote")
