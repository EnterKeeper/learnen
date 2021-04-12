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
