import marshmallow
from marshmallow import validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field, fields

from ..models.users import User


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ("hashed_password",)
        load_only = ("password",)

    email = auto_field(validate=validate.Email())
    username = auto_field(validate=validate.Length(min=User.min_username_length, max=User.max_username_length))
    bio = auto_field(validate=validate.Length(max=User.max_bio_length))
    password = auto_field("hashed_password")

    polls = fields.Nested("PollSchema", many=True, exclude=("author",))


class UserChangePasswordSchema(marshmallow.Schema):
    token = marshmallow.fields.String(required=True)
    old_password = marshmallow.fields.String(required=True)
    new_password = marshmallow.fields.String(required=True)


class UserChangePointsSchema(marshmallow.Schema):
    action = marshmallow.fields.Integer(required=True)
    count = marshmallow.fields.Integer(required=True)


class CustomEmailSchema(marshmallow.Schema):
    subject = marshmallow.fields.String(required=True)
    text = marshmallow.fields.String(required=True)
