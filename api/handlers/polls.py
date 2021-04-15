from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from marshmallow.exceptions import ValidationError
from flask_jwt_extended import get_jwt_identity, current_user

from ..database import db_session
from ..tools import errors
from ..models.polls import Poll, Option, Vote
from ..models.users import ModeratorGroup
from ..tools.response import make_success_message
from ..tools.decorators import user_required
from ..schemas.polls import PollSchema

blueprint = Blueprint(
    "polls_resource",
    __name__,
)
api = Api(blueprint)


class PollResource(Resource):
    def get(self, poll_id):
        session = db_session.create_session()

        poll = session.query(Poll).get(poll_id)
        if not poll:
            raise errors.PollNotFoundError

        data = PollSchema().dump(poll)
        return jsonify({"poll": data})

    @user_required()
    def put(self, poll_id):
        data = request.get_json()
        try:
            PollSchema(exclude=("options",)).load(data)
        except ValidationError as e:
            raise errors.InvalidRequestError(e.messages)

        session = db_session.create_session()
        poll = session.query(Poll).get(poll_id)
        if not poll:
            raise errors.PollNotFoundError

        user = current_user
        if poll.author_id != user.id and not ModeratorGroup.is_belong(user.group):
            raise errors.AccessDeniedError

        session.query(Poll).filter(Poll.id == user.id).update(data)
        session.commit()

        return make_success_message()

    @user_required()
    def delete(self, poll_id):
        session = db_session.create_session()
        poll = session.query(Poll).get(poll_id)
        if not poll:
            raise errors.PollNotFoundError

        user = current_user
        if poll.author_id != user.id and not ModeratorGroup.is_belong(user.group):
            raise errors.AccessDeniedError

        session.delete(poll)
        session.commit()

        return make_success_message()


class PollListResource(Resource):
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
            raise errors.InvalidRequestError(e.messages)

        session = db_session.create_session()

        options = data.pop("options")
        poll = Poll(**data)
        poll.author_id = get_jwt_identity()
        for option_data in options:
            poll.options.append(Option(**option_data))

        session.add(poll)
        session.commit()

        return make_success_message()


class PollVoteResource(Resource):
    @user_required()
    def post(self, option_id):
        session = db_session.create_session()

        option = session.query(Option).filter(Option.id == option_id).first()
        if not option:
            raise errors.OptionNotFoundError

        votes = session.query(Vote).join(Option).filter(Option.poll_id == option.poll_id, Vote.user_id == current_user.id).all()
        for vote in votes:
            session.delete(vote)
        new_vote = Vote(user_id=current_user.id, option_id=option_id)
        session.add(new_vote)
        session.commit()

        return make_success_message()


api.add_resource(PollResource, "/polls/<int:poll_id>")
api.add_resource(PollListResource, "/polls")
api.add_resource(PollVoteResource, "/polls/vote/<int:option_id>")
