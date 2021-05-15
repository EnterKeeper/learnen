from flask import Blueprint, render_template, redirect, make_response, url_for, flash
from flask_babel import _
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, unset_jwt_cookies, jwt_required, \
    get_jwt_identity, create_access_token, current_user

from qp.api.models.users import User, groups, ModeratorGroup, AdminGroup
from qp.api.tools import errors
from qp.forms.user import RegisterForm, LoginForm, UserProfileForm, UserEmailForm, UserChangePasswordForm, \
    UserChangeGroupForm, UserChangePointsForm, SendResetPasswordEmailForm, ResetPasswordForm
from qp.tools.api_requests import ApiGet, ApiPost, ApiPut
from qp.tools.images import save_image
from qp.tools.languages import INTERNAL_ERROR_MSG, NO_RIGHTS_ERROR_MSG, GROUPS

blueprint = Blueprint(
    "users",
    __name__,
)


@blueprint.route("/register", methods=["GET", "POST"])
@jwt_required(optional=True)
def register():
    if current_user:
        return redirect("/")

    form = RegisterForm()
    form.username.description = _("Length must be between ") + str(
        User.min_username_length) + _(" and ") + str(User.max_username_length)
    title = _("Sign up")
    if form.validate_on_submit():
        user_data = form.data.copy()
        for field in ("password_again", "submit", "csrf_token"):
            user_data.pop(field)
        response = ApiPost.make_request("register", json=user_data)

        if response.status_code == 200:
            flash(_("Your account has been created. You are now able to log in."), "success")
            return redirect(url_for("users.login"))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        elif errors.UserAlreadyExistsError.sub_code_match(code):
            flash(_("User already exists."), "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return render_template("register.html", title=title, form=form)


@blueprint.route("/login", methods=["GET", "POST"])
@jwt_required(optional=True)
def login():
    if current_user:
        return redirect("/")

    form = LoginForm()
    title = _("Login")
    if form.validate_on_submit():
        user_data = form.data.copy()
        for field in ("submit", "csrf_token"):
            user_data.pop(field)
        response = ApiPost.make_request("login", json=user_data)

        if response.status_code == 200:
            resp = make_response(redirect("/"))
            access_token, refresh_token = (response.json()[field] for field in ("access_token", "refresh_token"))
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            return resp

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        elif errors.UserNotFoundError.sub_code_match(code):
            flash(_("User not found."), "danger")
        elif errors.WrongCredentialsError.sub_code_match(code):
            flash(_("Wrong password."), "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return render_template("login.html", title=title, form=form)


@blueprint.route("/logout", methods=["GET"])
def logout():
    resp = redirect("/")
    unset_jwt_cookies(resp)
    flash(_("You have been logged out."), "warning")
    return resp


@blueprint.route("/token/refresh", methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    resp = make_response(redirect("/"))
    set_access_cookies(resp, access_token)
    return resp


@blueprint.route("/user/<username>")
@jwt_required(optional=True)
def user_info(username):
    data = ApiGet.make_request("users", username).json().get("user")
    title = _("User information")
    if data:
        data["polls"] = list(filter(lambda poll: not poll["private"], data["polls"]))
    return render_template("user_info.html", title=title, user=data)


@blueprint.route("/user/<username>/profile_settings", methods=['GET', 'POST'])
@jwt_required()
def profile_settings(username):
    if current_user.username != username and not ModeratorGroup.is_belong(current_user.group):
        return redirect(url_for("users.profile_settings", username=current_user.username))

    title = _("Profile settings")

    form = UserProfileForm()
    form.username.description = _("Length must be between ") + str(
        User.min_username_length) + _(" and ") + str(User.max_username_length)
    form.bio.description = _("Length cannot be longer than ") + str(User.max_bio_length)

    template_vars = dict(form=form, profile_tab="active", username=username)
    if form.validate_on_submit():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token", "avatar"):
            form_data.pop(field)

        if form.avatar.data:
            user_data = ApiGet.make_request("users", username).json()
            last_avatar_filename = user_data.get("user", dict()).get("avatar_filename", None)
            form_data["avatar_filename"] = save_image(form.avatar.data, remove=last_avatar_filename)

        response = ApiPut.make_request("users", username, "profile", json=form_data)
        if response.status_code == 200:
            flash(_("Profile settings have been updated."), "success")
            return redirect(url_for("users.profile_settings", username=form.username.data))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

        return render_template("user_profile_edit.html", title=title, **template_vars)

    user_data = ApiGet.make_request("users", username).json()
    if "user" not in user_data:
        return redirect("/")
    user_data = user_data["user"]
    form.username.data = user_data["username"]
    if user_data["bio"]:
        form.bio.data = user_data["bio"]

    return render_template("user_profile_edit.html", title=title, **template_vars)


@blueprint.route("/user/<username>/email_settings", methods=['GET', 'POST'])
@jwt_required()
def email_settings(username):
    if current_user.username != username:
        return redirect(url_for("users.email_settings", username=current_user.username))

    title = _("Change email")

    form = UserEmailForm()
    template_vars = dict(form=form, email_tab="active", username=username)
    if form.validate_on_submit():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token"):
            form_data.pop(field)

        response = ApiPut.make_request("users", username, "email", json=form_data)
        if response.status_code == 200:
            flash(_("Email has been updated."), "success")
            return redirect(url_for("users.email_settings", username=username))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    user_data = ApiGet.make_request("users", username).json()
    if "user" not in user_data or "email" not in user_data["user"]:
        return redirect("/")
    user_data = user_data["user"]
    form.email.data = user_data["email"]

    return render_template("user_email_edit.html", title=title, user=user_data, **template_vars)


@blueprint.route("/user/<username>/security_settings", methods=['GET', 'POST'])
@jwt_required()
def security_settings(username):
    if current_user.username != username:
        return redirect(url_for("users.security_settings", username=current_user.username))

    title = _("Security settings")

    form = UserChangePasswordForm()
    template_vars = dict(form=form, security_tab="active", username=username)
    if form.validate_on_submit():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token", "new_password_again"):
            form_data.pop(field)

        response = ApiPut.make_request("users", username, "change_password", json=form_data)
        if response.status_code == 200:
            flash(_("Your password has been updated."), "success")
            return redirect(url_for("users.security_settings", username=username))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        elif errors.WrongOldPasswordError.sub_code_match(code):
            flash(_("Old password is wrong."), "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return render_template("user_security_edit.html", title=title, **template_vars)


@blueprint.route("/user/<username>/verify", methods=['GET', 'POST'])
@jwt_required()
def user_verify(username):
    resp = ApiPut.make_request("users", username, "verify")
    if resp.status_code == 200:
        flash(_("User has been verified."), "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash(NO_RIGHTS_ERROR_MSG, "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return redirect(url_for("users.user_info", username=username))


@blueprint.route("/user/<username>/cancel_verification", methods=['GET', 'POST'])
@jwt_required()
def user_cancel_verification(username):
    resp = ApiPut.make_request("users", username, "cancel_verification")
    if resp.status_code == 200:
        flash(_("User's verification has been canceled."), "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash(NO_RIGHTS_ERROR_MSG, "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return redirect(url_for("users.user_info", username=username))


@blueprint.route("/user/<username>/ban", methods=['GET', 'POST'])
@jwt_required()
def user_ban(username):
    resp = ApiPut.make_request("users", username, "ban")
    if resp.status_code == 200:
        flash(_("User has been banned."), "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash(NO_RIGHTS_ERROR_MSG, "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return redirect(url_for("users.user_info", username=username))


@blueprint.route("/user/<username>/unban", methods=['GET', 'POST'])
@jwt_required()
def user_unban(username):
    resp = ApiPut.make_request("users", username, "unban")
    if resp.status_code == 200:
        flash(_("User has been unbanned."), "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash(NO_RIGHTS_ERROR_MSG, "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return redirect(url_for("users.user_info", username=username))


@blueprint.route("/user/<username>/change_group", methods=['GET', 'POST'])
@jwt_required()
def user_change_group(username):
    user = ApiGet.make_request("users", username).json().get("user")
    if not AdminGroup.is_belong(current_user.group) or current_user.group <= user["group"]:
        flash(NO_RIGHTS_ERROR_MSG, "danger")
        return redirect(url_for("users.user_info", username=username))

    title = _("Change group")

    form = UserChangeGroupForm()
    if form.is_submitted():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token"):
            form_data.pop(field)

        response = ApiPut.make_request("users", username, "change_group", json=form_data)
        if response.status_code == 200:
            flash(_("User's group has been updated."), "success")
            return redirect(url_for("users.user_change_group", username=username))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    if user:
        form.group.choices = [(group.id, GROUPS[group]) for group in groups if current_user.group > group.id]
        form.group.default = user["group"]
        form.process()

    return render_template("user_change_group.html", title=title, form=form, user=user)


@blueprint.route("/user/<username>/manage_polls")
@jwt_required()
def user_manage_polls(username):
    if not (current_user.username == username and ModeratorGroup.is_belong(current_user.group)):
        return redirect(url_for("users.user_info", username=username))

    title = _("User's polls")

    polls = ApiGet.make_request("users", username, "polls").json().get("polls")
    if not polls:
        return redirect(url_for("users.user_info", username=username))
    for poll in polls:
        poll["participants"] = sum([len(option["users"]) for option in poll["options"]])
    return render_template("user_manage_polls.html", title=title, polls=polls)


@blueprint.route("/user/<username>/change_points", methods=['GET', 'POST'])
@jwt_required()
def user_change_points(username):
    if not ModeratorGroup.is_belong(current_user.group):
        flash(NO_RIGHTS_ERROR_MSG, "danger")
        return redirect(url_for("users.user_info", username=username))

    title = _("Change points")

    form = UserChangePointsForm()
    if form.validate_on_submit():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token"):
            form_data.pop(field)

        response = ApiPut.make_request("users", username, "change_points", json=form_data)
        if response.status_code == 200:
            flash(_("User's points has been updated."), "success")
            return redirect(url_for("users.user_change_points", username=username))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return render_template("user_change_points.html", title=title, form=form)


@blueprint.route("/users")
@jwt_required()
def users_list():
    title = _("Registered users")

    users = ApiGet.make_request("users").json().get("users")
    if not users:
        return redirect("/")
    return render_template("users_list.html", title=title, users=users)


@blueprint.route("/reset_password", methods=['GET', 'POST'])
@jwt_required(optional=True)
def send_reset_password_email():
    if current_user:
        return redirect("/")

    title = _("Reset password")

    form = SendResetPasswordEmailForm()
    if form.validate_on_submit():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token"):
            form_data.pop(field)

        response = ApiPost.make_request("send_reset_password_email", json=form_data)
        if response.status_code == 200:
            flash(_("An email with instructions has been sent. Check your mailbox."), "success")
            return redirect(url_for("users.login"))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        elif errors.UserNotFoundError.sub_code_match(code):
            flash(_("User not found."), "danger")
        elif errors.SendingEmailError.sub_code_match(code):
            flash(_("Failed sending email."), "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return render_template("send_reset_password_email.html", title=title, form=form)


@blueprint.route("/reset_password/<token>", methods=['GET', 'POST'])
@jwt_required(optional=True)
def reset_password(token):
    if current_user:
        return redirect("/")

    title = _("Reset password")

    form = ResetPasswordForm()
    if form.validate_on_submit():
        form_data = form.data.copy()
        form_data["token"] = token
        for field in ("submit", "csrf_token", "new_password_again"):
            form_data.pop(field)

        response = ApiPost.make_request("reset_password", json=form_data)
        if response.status_code == 200:
            flash(_("Your password has been updated."), "success")
            return redirect(url_for("users.login"))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        elif errors.UserNotFoundError.sub_code_match(code):
            flash(_("User not found."), "danger")
        elif errors.SendingEmailError.sub_code_match(code):
            flash(_("Failed sending email."), "danger")
        elif errors.InvalidResetPasswordTokenError.sub_code_match(code):
            flash(_("Invalid link."), "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")

    return render_template("reset_password.html", title=title, form=form)


@blueprint.route("/confirm_email", methods=['GET', 'POST'])
@jwt_required()
def send_confirmation_email():
    response = ApiPost.make_request("send_confirmation_email")
    if response.status_code == 200:
        flash(_("An email with instructions has been sent. Check your mailbox."), "success")
    else:
        error = response.json()["error"]
        code = error["code"]

        if errors.EmailAlreadyConfirmedError.sub_code_match(code):
            flash(_("Email already confirmed."), "danger")
        elif errors.SendingEmailError.sub_code_match(code):
            flash(_("Failed sending email."), "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")
    return redirect(url_for("users.email_settings", username=current_user.username))


@blueprint.route("/confirm_email/<token>", methods=['GET', 'POST'])
@jwt_required(optional=True)
def confirm_email(token):
    response = ApiPost.make_request("confirm_email", json=dict(token=token))
    if response.status_code == 200:
        flash(_("Email has been confirmed."), "success")
    else:
        error = response.json()["error"]
        code = error["code"]

        if errors.UserNotFoundError.sub_code_match(code):
            flash(_("User not found."), "danger")
        elif errors.SendingEmailError.sub_code_match(code):
            flash(_("Failed sending email."), "danger")
        elif errors.InvalidResetPasswordTokenError.sub_code_match(code):
            flash(_("Invalid link."), "danger")
        else:
            flash(INTERNAL_ERROR_MSG, "danger")
    target = url_for("users.email_settings", username=current_user.username) if current_user \
        else url_for("default.index")
    return redirect(target)
