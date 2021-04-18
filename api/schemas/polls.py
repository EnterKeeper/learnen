from marshmallow import validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field, fields

from ..models.polls import Poll, Option, Comment
from .users import UserSchema


class OptionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Option

    title = auto_field(validate=validate.Length(min=1, max=Option.max_title_length))
    users = auto_field()


class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comment

    text = auto_field(validate=validate.Length(min=1, max=Comment.max_text_length))
    user = fields.Nested(UserSchema, exclude=("email", "polls"))


class PollSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Poll
        dump_only = ("id", "author_id", "completed", "created_at", "comments", "author")

    title = auto_field(validate=validate.Length(min=1, max=Poll.max_title_length))
    description = auto_field(validate=validate.Length(min=1, max=Poll.max_description_length))
    author = fields.Nested(UserSchema, exclude=("email", "polls"))
    options = fields.Nested(OptionSchema, many=True, required=True,
                            validate=validate.Length(min=Poll.min_options_count, max=Poll.max_options_count))
    comments = fields.Nested(CommentSchema, many=True)
