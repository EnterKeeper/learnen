from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import get_jwt_identity, current_user

from data import api_errors
from data import db_session
from data.polls import Poll, Option
from data.groups import ModeratorGroup
from tools.response import make_success_message
from tools.api_decorators import user_required
from schemas.polls import PollSchema

blueprint = Blueprint(
    "polls_resource",
    __name__,
)
api = Api(blueprint)


class PollResource(Resource):
    @user_required()
    def get(self, poll_id):
        session = db_session.create_session()

        poll = session.query(Poll).get(poll_id)
        if not poll:
            raise api_errors.PollNotFoundError

        data = PollSchema().dump(poll)
        return jsonify({"poll": data})

    @user_required()
    def put(self, poll_id):
        data = request.get_json()
        try:
            PollSchema(exclude=("options",)).load(data)
        except ValidationError as e:
            raise api_errors.InvalidRequestError(e.messages)

        session = db_session.create_session()
        poll = session.query(Poll).get(poll_id)
        if not poll:
            raise api_errors.PollNotFoundError

        user = current_user
        if poll.author_id != user.id and not ModeratorGroup.is_allowed(user.group):
            raise api_errors.AccessDeniedError

        session.query(Poll).filter(Poll.id == user.id).update(data)
        session.commit()

        return make_success_message()

    @user_required()
    def delete(self, poll_id):
        session = db_session.create_session()
        poll = session.query(Poll).get(poll_id)
        if not poll:
            raise api_errors.PollNotFoundError

        user = current_user
        if poll.author_id != user.id and not ModeratorGroup.is_allowed(user.group):
            raise api_errors.AccessDeniedError

        session.delete(poll)
        session.commit()

        return make_success_message()


class PollListResource(Resource):
    @user_required()
    def get(self):
        session = db_session.create_session()
        polls = session.query(Poll).all()
        return jsonify({
            "polls": PollSchema().dump(polls, many=True)
        })

    @user_required()
    def post(self):
        data = request.get_json()
        try:
            PollSchema().load(data)
        except ValidationError as e:
            raise api_errors.InvalidRequestError(e.messages)

        session = db_session.create_session()

        options = data.pop("options")
        poll = Poll(**data)
        poll.author_id = get_jwt_identity()
        for option_data in options:
            poll.options.append(Option(**option_data))

        session.add(poll)
        session.commit()

        return make_success_message()


api.add_resource(PollResource, "/api/polls/<int:poll_id>")
api.add_resource(PollListResource, "/api/polls")
