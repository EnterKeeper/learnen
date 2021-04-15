from marshmallow import validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field, fields

from ..models.polls import Poll, Option, Comment
from .users import UserSchema


class OptionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Option

    users = auto_field()


class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comment

    user = fields.Nested(UserSchema, exclude=("email", "polls"))


class PollSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Poll
        dump_only = ("id", "author_id", "completed", "created_at", "comments", "author")

    author = fields.Nested(UserSchema, exclude=("email", "polls"))
    options = fields.Nested(OptionSchema, many=True, required=True, validate=validate.Length(min=1, max=20))
    comments = fields.Nested(CommentSchema, many=True)
