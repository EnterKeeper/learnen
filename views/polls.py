from flask import Blueprint, render_template, redirect, make_response, request
from flask_jwt_extended import jwt_required, current_user

from api.tools import errors
from tools.api_requests import ApiGet

blueprint = Blueprint(
    "polls",
    __name__,
)


@blueprint.route("/polls")
@jwt_required(optional=True)
def polls_list():
    polls = ApiGet.make_request("polls").json().get("polls")
    return render_template("polls.html", polls=polls)


@blueprint.route("/polls/<int:poll_id>")
@jwt_required(optional=True)
def poll_info(poll_id):
    pass
