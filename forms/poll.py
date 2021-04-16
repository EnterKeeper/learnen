from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, RadioField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class VoteForm(FlaskForm):
    options = RadioField("Options", coerce=int, choices=[], validators=[Optional()])
    vote_btn = SubmitField("Vote")


class LeaveCommentForm(FlaskForm):
    text = TextAreaField("Comment", validators=[DataRequired()])
    leave_comment_btn = SubmitField("Leave comment")
