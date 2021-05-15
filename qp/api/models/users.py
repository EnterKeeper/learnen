from datetime import datetime

from flask import current_app
import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedSerializer

from ..database.db_session import SqlAlchemyBase


def generate_password(password):
    return generate_password_hash(password)


class Points:
    register = 20
    create_poll = -10
    vote = 5

    @classmethod
    def check(cls, current_points, required_points):
        return (current_points + required_points) >= 0 or required_points >= 0


class User(SqlAlchemyBase):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    username = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)
    bio = sqlalchemy.Column(sqlalchemy.String)
    group = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    avatar_filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    verified = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    banned = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    points = sqlalchemy.Column(sqlalchemy.Integer, default=Points.register)

    polls = orm.relation("Poll", back_populates="author", order_by="desc(Poll.created_at)", passive_deletes=True)

    min_username_length = 4
    max_username_length = 20
    max_bio_length = 200

    def set_password(self, password):
        self.hashed_password = generate_password(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    @staticmethod
    def get_reset_token(user_id, expires=1800):
        s = TimedSerializer(current_app.secret_key, "user_id")
        return s.dumps(user_id)

    @staticmethod
    def get_reset_token_info(token, max_age=900):
        s = TimedSerializer(current_app.secret_key, 'user_id')
        try:
            return s.loads(token, max_age=max_age)
        except Exception as e:
            return None

    def __repr__(self):
        return f"<User> {self.id} {self.username}"


class UserGroup:
    id = 0
    title = "User"

    @classmethod
    def is_belong(cls, user_group_id):
        return user_group_id >= cls.id


class ModeratorGroup(UserGroup):
    id = 1
    title = "Moderator"


class AdminGroup(UserGroup):
    id = 10
    title = "Admin"


class OwnerGroup(UserGroup):
    id = 100
    title = "Owner"


groups = (UserGroup, ModeratorGroup, AdminGroup, OwnerGroup)


def get_group(id=None, title=None):
    for group in groups:
        if group.id == id or group.title == title:
            return group
    return None
