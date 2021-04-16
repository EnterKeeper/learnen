from flask import Blueprint, render_template, redirect, make_response, request, flash, url_for
from flask_jwt_extended import jwt_required, current_user

from api.tools import errors
from forms.poll import VoteForm, LeaveCommentForm
from tools.api_requests import ApiGet, ApiPost

blueprint = Blueprint(
    "polls",
    __name__,
)


@blueprint.route("/polls")
@jwt_required(optional=True)
def polls_list():
    polls = ApiGet.make_request("polls").json().get("polls")
    return render_template("polls.html", polls=polls)


@blueprint.route("/polls/<int:poll_id>", methods=["GET", "POST"])
@jwt_required(optional=True)
def poll_info(poll_id):
    vote_form = VoteForm()
    leave_comment_form = LeaveCommentForm()
    title = "Poll"

    if vote_form.vote_btn.data and vote_form.options.data is not None:
        resp = ApiPost.make_request("polls", "vote", vote_form.options.data)
        if resp.status_code == 200:
            flash("You have successfully voted", "success")
            return redirect(url_for("polls.poll_info", poll_id=poll_id))

        flash("Internal error. Try again.", "danger")

    if leave_comment_form.leave_comment_btn.data and leave_comment_form.validate():
        form_data = leave_comment_form.data.copy()
        for field in ("csrf_token", "leave_comment_btn"):
            form_data.pop(field)
        resp = ApiPost.make_request("polls", poll_id, "comment", json=form_data)
        if resp.status_code == 200:
            return redirect(url_for("polls.poll_info", poll_id=poll_id))

        flash("Internal error. Try again.", "danger")

    poll = ApiGet.make_request("polls", poll_id).json().get("poll")
    if poll:
        title = poll["title"]
        for option in poll.get("options"):
            value = option["id"]
            vote_form.options.choices.append((value, option["title"]))
            if current_user and current_user.id in option["users"]:
                vote_form.options.default = value
        vote_form.process()
    return render_template("poll_info.html", poll=poll, title=title, vote_form=vote_form, leave_comment_form=leave_comment_form)
