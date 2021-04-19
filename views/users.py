from flask import Blueprint, render_template, redirect, make_response, url_for, flash
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, unset_jwt_cookies, jwt_required, \
    get_jwt_identity, create_access_token, current_user

from api.tools import errors
from api.models.users import ModeratorGroup
from forms.user import RegisterForm, LoginForm, UserProfileForm, UserEmailForm, UserChangePasswordForm
from tools.api_requests import ApiGet, ApiPost, ApiPut
from tools.images import save_image

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
    title = "Sign up"
    if form.validate_on_submit():
        user_data = form.data.copy()
        for field in ("password_again", "submit", "csrf_token"):
            user_data.pop(field)
        response = ApiPost.make_request("register", json=user_data)

        if response.status_code == 200:
            flash("Your account has been created. You are now able to log in", "success")
            return redirect(url_for("users.login"))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        elif errors.UserAlreadyExistsError.sub_code_match(code):
            flash("User already exists.", "danger")
        else:
            flash("Internal error. Try again.", "danger")

    return render_template("register.html", title=title, form=form)


@blueprint.route("/login", methods=["GET", "POST"])
@jwt_required(optional=True)
def login():
    if current_user:
        return redirect("/")

    form = LoginForm()
    title = "Login"
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
            flash("User not found.", "danger")
        elif errors.WrongCredentialsError.sub_code_match(code):
            flash("Wrong password.", "danger")
        else:
            flash("Internal error. Try again.", "danger")

    return render_template("login.html", title=title, form=form)


@blueprint.route("/logout", methods=["GET"])
def logout():
    resp = redirect("/")
    unset_jwt_cookies(resp)
    flash("You have been logged out.", "warning")
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
    if data:
        data["polls"] = list(filter(lambda poll: not poll["private"], data["polls"]))
    return render_template("user_info.html", title=f"User information", user=data)


@blueprint.route("/user/<username>/profile_settings", methods=['GET', 'POST'])
@jwt_required()
def profile_settings(username):
    if current_user.username != username and not ModeratorGroup.is_belong(current_user.group):
        return redirect(url_for("users.profile_settings", username=current_user.username))

    title = "Profile settings"

    form = UserProfileForm()
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
            flash("Profile settings has been updated.", "success")
            return redirect(url_for("users.profile_settings", username=form.username.data))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        elif errors.UserNotFoundError.sub_code_match(code):
            flash("User not found", "danger")
        else:
            flash("Internal error. Try again.", "danger")

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

    title = "Change email"

    form = UserEmailForm()
    template_vars = dict(form=form, email_tab="active", username=username)
    if form.validate_on_submit():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token"):
            form_data.pop(field)

        response = ApiPut.make_request("users", username, "email", json=form_data)
        if response.status_code == 200:
            flash("Email has been updated.", "success")
            return redirect(url_for("users.email_settings", username=username))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        elif errors.UserNotFoundError.sub_code_match(code):
            flash("User not found", "danger")
        else:
            flash("Internal error. Try again.", "danger")

    user_data = ApiGet.make_request("users", username).json()
    if "user" not in user_data or "email" not in user_data["user"]:
        return redirect("/")
    email = user_data["user"]["email"]
    form.email.data = email

    return render_template("user_email_edit.html", title=title, **template_vars)


@blueprint.route("/user/<username>/security_settings", methods=['GET', 'POST'])
@jwt_required()
def security_settings(username):
    if current_user.username != username:
        return redirect(url_for("users.security_settings", username=current_user.username))

    title = "Security settings"

    form = UserChangePasswordForm()
    template_vars = dict(form=form, security_tab="active", username=username)
    if form.validate_on_submit():
        form_data = form.data.copy()
        for field in ("submit", "csrf_token", "new_password_again"):
            form_data.pop(field)

        response = ApiPut.make_request("users", username, "change_password", json=form_data)
        if response.status_code == 200:
            flash("Your password has been updated.", "success")
            return redirect(url_for("users.security_settings", username=username))

        error = response.json()["error"]
        code = error["code"]

        if errors.InvalidRequestError.sub_code_match(code):
            fields = error["fields"]
            for field in fields:
                if field in form:
                    form[field].errors += fields[field]
        elif errors.UserNotFoundError.sub_code_match(code):
            flash("User not found", "danger")
        elif errors.WrongOldPassword.sub_code_match(code):
            flash("Old password is wrong.", "danger")
        else:
            flash("Internal error. Try again.", "danger")

    return render_template("user_security_edit.html", title=title, **template_vars)


@blueprint.route("/user/<username>/verify", methods=['GET', 'POST'])
@jwt_required()
def user_verify(username):
    resp = ApiPut.make_request("users", username, "verify")
    if resp.status_code == 200:
        flash("User has been verified.", "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash("You have no rights to do this.", "danger")
        else:
            flash("Internal error. Try again.", "danger")

    return redirect(url_for("users.user_info", username=username))


@blueprint.route("/user/<username>/cancel_verification", methods=['GET', 'POST'])
@jwt_required()
def user_cancel_verification(username):
    resp = ApiPut.make_request("users", username, "cancel_verification")
    if resp.status_code == 200:
        flash("User's verification has been canceled.", "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash("You have no rights to do this.", "danger")
        else:
            flash("Internal error. Try again.", "danger")

    return redirect(url_for("users.user_info", username=username))


@blueprint.route("/user/<username>/ban", methods=['GET', 'POST'])
@jwt_required()
def user_ban(username):
    resp = ApiPut.make_request("users", username, "ban")
    if resp.status_code == 200:
        flash("User has been banned.", "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash("You have no rights to do this.", "danger")
        else:
            flash("Internal error. Try again.", "danger")

    return redirect(url_for("users.user_info", username=username))


@blueprint.route("/user/<username>/unban", methods=['GET', 'POST'])
@jwt_required()
def user_unban(username):
    resp = ApiPut.make_request("users", username, "unban")
    if resp.status_code == 200:
        flash("User has been unbanned.", "success")
    else:
        error = resp.json()["error"]
        code = error["code"]
        if errors.AccessDeniedError.sub_code_match(code):
            flash("You have no rights to do this.", "danger")
        else:
            flash("Internal error. Try again.", "danger")

    return redirect(url_for("users.user_info", username=username))
