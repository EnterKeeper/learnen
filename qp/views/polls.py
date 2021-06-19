from flask import Blueprint, render_template, redirect, flash, url_for
from flask_babel import _
from flask_jwt_extended import jwt_required, current_user

from qp.api.models.polls import Poll, Option, Comment
from qp.api.models.users import ModeratorGroup
from qp.api.tools import errors
from qp.forms.poll import CreatePollForm, EditPollForm, VoteForm, LeaveCommentForm, EditCommentForm
from qp.tools.api_requests import ApiGet, ApiPost, ApiPut, ApiDelete
from qp.tools.languages import INTERNAL_ERROR_MSG, NO_RIGHTS_ERROR_MSG

blueprint = Blueprint(
    "polls",
    __name__,
)


@blueprint.route("/polls")
@jwt_required(optional=True)
def polls_list():
    title = _("Polls")
    polls = ApiGet.make_request("polls").json().get("polls")
    if polls:
        polls = list(filter(lambda poll: not poll["private"] and not poll["deleted"], polls))
        for poll in polls:
            poll["participants"] = sum([len(option["users"]) for option in poll["options"]])
    return render_template("polls.html", title=title, polls=polls)


@blueprint.route("/polls/<int:poll_id>", methods=["GET", "POST"])
@jwt_required(optional=True)
def poll_info(poll_id):
    title = _("Poll")

    vote_form = VoteForm()
    leave_comment_form = LeaveCommentForm()
    leave_comment_form.text.description = _("Length cannot be longer than ") + str(Comment.max_text_length)

    if vote_form.vote_btn.data and vote_form.options.data is not None:
        resp = ApiPost.make_request("polls", "vote", vote_form.options.data)
        if resp.status_code == 200:
            flash(_("You have successfully voted"), "success")
            return redirect(url_for("polls.poll_info", poll_id=poll_id))

        flash(INTERNAL_ERROR_MSG, "danger")

    if leave_comment_form.leave_comment_btn.data and leave_comment_form.validate():
        form_data = leave_comment_form.data.copy()
        for field in ("csrf_token", "leave_comment_btn"):
            form_data.pop(field)
        resp = ApiPost.make_request("polls", poll_id, "comment", json=form_data)
        if resp.status_code == 200:
            return redirect(url_for("polls.poll_info", poll_id=poll_id))

        flash(INTERNAL_ERROR_MSG, "danger")

    poll = ApiGet.make_request("polls", poll_id).json().get("poll")
    user_voted = False
    if poll:
        title = poll["title"]
        users_count = 0
        for option in poll.get("options"):
            option["users_count"] = len(option["users"])
            users_count += option["users_count"]

            value = option["id"]
            vote_form.options.choices.append((value, option["title"]))
            if current_user and current_user.id in option["users"]:
                vote_form.options.default = value
                user_voted = True
        vote_form.process()

        poll["users_count"] = users_count
        for option in poll.get("options"):
            option["percent"] = int(option["users_count"] / users_count * 100) if users_count else 0
    return render_template("poll_info.html", poll=poll, title=title,
                           vote_form=vote_form, leave_comment_form=leave_comment_form, user_voted=user_voted)


@blueprint.route("/polls/<int:poll_id>/edit", methods=["GET", "POST"])
@jwt_required()
def poll_edit(poll_id):
    form = EditPollForm()
    title = _("Edit poll")
    form.title.description = _("Length cannot be longer than ") + str(Poll.max_title_length)
    form.description.description = _("Length cannot be longer than ") + str(Poll.max_description_length)

    if form.validate_on_submit():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token"):
            form_data.pop(field)

        resp = ApiPut.make_request("polls", poll_id, json=form_data)
        if resp.status_code == 200:
            flash(_("Poll has been successfully updated."), "success")
            return redirect(url_for("polls.poll_edit", poll_id=poll_id))

        error = resp.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    poll = ApiGet.make_request("polls", poll_id).json().get("poll")
    if poll:
        form.title.data = poll["title"]
        form.description.data = poll["description"]
        form.private.data = poll["private"]

        if current_user.id != poll["author"]["id"] and not ModeratorGroup.is_belong(current_user.group):
            return redirect(url_for("polls.poll_info", poll_id=poll_id))

    return render_template("poll_edit.html", title=title, form=form, poll=poll)


@blueprint.route("/polls/<int:poll_id>/delete", methods=["GET", "POST"])
@jwt_required()
def poll_delete(poll_id):
    resp = ApiDelete.make_request("polls", poll_id)
    if resp.status_code == 200:
        flash(_("Poll has been deleted."), "success")
        return redirect(url_for("polls.polls_list"))

    error = resp.json()["error"]
    code = error["code"]
    if errors.AccessDeniedError.sub_code_match(code):
        flash(NO_RIGHTS_ERROR_MSG, "danger")
    else:
        flash(INTERNAL_ERROR_MSG, "danger")

    return redirect(url_for("polls.poll_info", poll_id=poll_id))


@blueprint.route("/polls/create", methods=["GET", "POST"])
@jwt_required()
def poll_create():
    if not current_user:
        return redirect(url_for("polls.polls_list"))
    title = _("Create poll")
    form = CreatePollForm()
    form.title.description = _("Length cannot be longer than ") + str(Poll.max_title_length)
    form.description.description = _("Length cannot be longer than ") + str(Poll.max_description_length)
    form.options.description = _("Every option's length cannot be longer than ") + str(Option.max_title_length)

    if form.validate_on_submit():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token"):
            form_data.pop(field)
        for i, option_title in enumerate(form_data["options"]):
            form_data["options"][i] = {"title": option_title}

        resp = ApiPost.make_request("polls", json=form_data)
        if resp.status_code == 200:
            flash(_("Poll has been created."), "success")
            return redirect(url_for("polls.poll_info", poll_id=resp.json()["poll"]["id"]))

        error = resp.json()["error"]
        code = error["code"]

        if errors.NotEnoughPointsError.sub_code_match(code):
            flash(_("Not enough points to create poll."), "danger")
        elif errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return render_template("poll_create.html", title=title, form=form)


@blueprint.route("/polls/<int:poll_id>/complete", methods=["GET", "POST"])
@jwt_required()
def poll_complete(poll_id):
    resp = ApiPut.make_request("polls", poll_id, "complete")
    if resp.status_code == 200:
        flash(_("Poll has been completed."), "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash(NO_RIGHTS_ERROR_MSG, "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return redirect(url_for("polls.poll_info", poll_id=poll_id))


@blueprint.route("/polls/<int:poll_id>/resume", methods=["GET", "POST"])
@jwt_required()
def poll_resume(poll_id):
    resp = ApiPut.make_request("polls", poll_id, "resume")
    if resp.status_code == 200:
        flash(_("Poll has been resumed."), "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash(NO_RIGHTS_ERROR_MSG, "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return redirect(url_for("polls.poll_info", poll_id=poll_id))


@blueprint.route("/polls/<int:poll_id>/comments/<int:comment_id>/delete", methods=["GET", "POST"])
@jwt_required()
def comment_delete(poll_id, comment_id):
    resp = ApiDelete.make_request("comments", comment_id)
    if resp.status_code == 200:
        flash(_("Comment has been deleted."), "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash(NO_RIGHTS_ERROR_MSG, "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return redirect(url_for("polls.poll_info", poll_id=poll_id))


@blueprint.route("/polls/<int:poll_id>/comments/<int:comment_id>/edit", methods=['GET', 'POST'])
@jwt_required()
def comment_edit(poll_id, comment_id):
    comment = ApiGet.make_request("comments", comment_id).json().get("comment")
    if current_user.id != comment["user"]["id"]:
        flash(NO_RIGHTS_ERROR_MSG, "danger")
        return redirect(url_for("polls.poll_info", poll_id=poll_id))

    title = _("Edit comment")

    form = EditCommentForm()
    form.text.description = _("Length cannot be longer than ") + str(Comment.max_text_length)
    if form.validate_on_submit():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token"):
            form_data.pop(field)

        response = ApiPut.make_request("comments", comment_id, json=form_data)
        if response.status_code == 200:
            flash(_("Comment has been updated."), "success")
            return redirect(url_for("polls.poll_info", poll_id=poll_id))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    if comment:
        form.text.data = comment["text"]

    return render_template("comment_edit.html", title=title, form=form, comment=comment, poll_id=poll_id)
