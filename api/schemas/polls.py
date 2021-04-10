from marshmallow import validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field, fields

from ..data.polls import Poll, Option, Comment
from ..schemas.users import UserSchema


class OptionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Option
        exclude = ("id",)

    users = auto_field()


class CommentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Comment

    user = fields.Nested(UserSchema, exclude=("email",))


class PollSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Poll
        dump_only = ("id", "author_id", "completed", "created_at", "comments")

    options = fields.Nested(OptionSchema, many=True, required=True, validate=validate.Length(min=1))
    comments = fields.Nested(CommentSchema, many=True)
