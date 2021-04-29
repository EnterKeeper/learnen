from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, TextAreaField, BooleanField, SubmitField, FieldList
from wtforms.validators import DataRequired, Length, Optional

from qp.api.models.polls import Poll, Option, Comment


class CreatePollForm(FlaskForm):
    title = StringField(lazy_gettext("Title"), validators=[DataRequired(), Length(max=Poll.max_title_length)])
    description = TextAreaField(lazy_gettext("Description"), validators=[Length(max=Poll.max_description_length)])
    options = FieldList(StringField("Option", validators=[DataRequired(), Length(max=Option.max_title_length)]),
                        validators=[Length(min=Poll.min_options_count, max=Poll.max_options_count)])
    private = BooleanField(lazy_gettext("Is private (available only via link)"))
    submit = SubmitField(lazy_gettext("Create"))


class EditPollForm(FlaskForm):
    title = StringField(lazy_gettext("Title"), validators=[DataRequired(), Length(max=Poll.max_title_length)])
    description = TextAreaField(lazy_gettext("Description"), validators=[Length(max=Poll.max_description_length)])
    private = BooleanField(lazy_gettext("Is private (available only via link)"))
    submit = SubmitField(lazy_gettext("Update"))


class VoteForm(FlaskForm):
    options = RadioField(lazy_gettext("Options"), coerce=int, choices=[], validators=[Optional()])
    vote_btn = SubmitField(lazy_gettext("Vote"))


class LeaveCommentForm(FlaskForm):
    text = TextAreaField(lazy_gettext("Comment"), validators=[DataRequired(), Length(max=Comment.max_text_length)])
    leave_comment_btn = SubmitField(lazy_gettext("Leave comment"))


class EditCommentForm(FlaskForm):
    text = TextAreaField(lazy_gettext("Comment"), validators=[DataRequired(), Length(max=Comment.max_text_length)])
    submit = SubmitField(lazy_gettext("Update comment"))
