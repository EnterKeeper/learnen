from datetime import datetime

import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from ..database.db_session import SqlAlchemyBase


def generate_password(password):
    return generate_password_hash(password)


class User(SqlAlchemyBase):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    username = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    bio = sqlalchemy.Column(sqlalchemy.String)
    group = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    avatar_filename = sqlalchemy.Column(sqlalchemy.String, default="default.png")

    polls = orm.relation("Poll", back_populates="author", passive_deletes=True)

    min_username_length = 4
    max_username_length = 20
    max_bio_length = 200

    def set_password(self, password):
        self.hashed_password = generate_password(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

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


groups = (UserGroup, ModeratorGroup, AdminGroup)


def get_group(id=None, title=None):
    for group in groups:
        if group.id == id or group.title == title:
            return group
    return None
