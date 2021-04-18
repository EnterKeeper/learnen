from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, TextAreaField, SubmitField, FieldList
from wtforms.validators import DataRequired, Length, Optional


class CreatePollForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description")
    options = FieldList(StringField("Option", validators=[DataRequired()]))
    submit = SubmitField("Create")


class EditPollForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField("Update")


class VoteForm(FlaskForm):
    options = RadioField("Options", coerce=int, choices=[], validators=[Optional()])
    vote_btn = SubmitField("Vote")


class LeaveCommentForm(FlaskForm):
    text = TextAreaField("Comment", validators=[DataRequired()])
    leave_comment_btn = SubmitField("Leave comment")
