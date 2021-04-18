from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, TextAreaField, BooleanField, SubmitField, FieldList
from wtforms.validators import DataRequired, Length, Optional

from api.models.polls import Poll, Option, Comment


class CreatePollForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=Poll.max_title_length)],
                        description=f"Length cannot be longer than {Poll.max_title_length}")
    description = TextAreaField("Description", validators=[Length(max=Poll.max_description_length)],
                                description=f"Length cannot be longer than {Poll.max_description_length}")
    options = FieldList(StringField("Option", validators=[DataRequired(), Length(max=Option.max_title_length)]),
                        validators=[Length(min=Poll.min_options_count, max=Poll.max_options_count)],
                        description=f"Every option's length cannot be longer than {Option.max_title_length}")
    private = BooleanField("Is private (available only via link)")
    submit = SubmitField("Create")


class EditPollForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=Poll.max_title_length)],
                        description=f"Length cannot be longer than {Poll.max_title_length}")
    description = TextAreaField("Description", validators=[Length(max=Poll.max_description_length)],
                                description=f"Length cannot be longer than {Poll.max_description_length}")
    private = BooleanField("Is private (available only via link)")
    submit = SubmitField("Update")


class VoteForm(FlaskForm):
    options = RadioField("Options", coerce=int, choices=[], validators=[Optional()])
    vote_btn = SubmitField("Vote")


class LeaveCommentForm(FlaskForm):
    text = TextAreaField("Comment", validators=[DataRequired(), Length(max=Comment.max_text_length)],
                         description=f"Length cannot be longer than {Comment.max_text_length}")
    leave_comment_btn = SubmitField("Leave comment")
