from datetime import datetime

import sqlalchemy
from sqlalchemy import orm

from data.db_session import SqlAlchemyBase
from data.users import User


class Poll(SqlAlchemyBase):
    __tablename__ = "polls"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id), nullable=False)
    completed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)

    author_obj = orm.relation(User)
    options = orm.relation("Option", back_populates="poll_obj")
    comments = orm.relation("Comment", back_populates="poll_obj")

    def __repr__(self):
        return f"<Poll> {self.id} {self.title}"


class Option(SqlAlchemyBase):
    __tablename__ = "options"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    poll = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(Poll.id), nullable=False)

    poll_obj = orm.relation(Poll)
    users = orm.relation(User, secondary="votes")

    def __repr__(self):
        return f"<Option> {self.id} {self.title} ({self.poll_obj.title})"


class Vote(SqlAlchemyBase):
    __tablename__ = "votes"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True, autoincrement=True)
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id), nullable=False)
    option = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(Option.id), nullable=False)

    user_obj = orm.relation(User)
    option_obj = orm.relation(Option)

    def __repr__(self):
        return f"<Vote> {self.id} {self.user_obj.username} {self.option_obj.title} ({self.option_obj.poll_obj.title})"


class Comment(SqlAlchemyBase):
    __tablename__ = "comments"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True, autoincrement=True)
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id), nullable=False)
    poll = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(Poll.id), nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    user_obj = orm.relation(User)
    poll_obj = orm.relation(Poll)

    def __repr__(self):
        return f"<Comment> {self.id} {self.user_obj.username})"
