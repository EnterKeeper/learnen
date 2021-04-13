from flask import Blueprint, render_template, redirect, make_response, url_for
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, unset_jwt_cookies, jwt_required, \
    get_jwt_identity, create_access_token, current_user

from api.tools import errors
from api.models.users import ModeratorGroup
from forms.user import RegisterForm, LoginForm, UserProfileForm
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
        if form.password.data != form.password_again.data:
            return render_template("register.html", title=title, form=form, message="Passwords dont match")
        user_data = form.data.copy()
        for field in ("password_again", "submit", "csrf_token"):
            user_data.pop(field)
        response = ApiPost.make_request("register", json=user_data)

        if response.status_code != 200:
            error = response.json()["error"]
            code = error["code"]

            message = ""
            if errors.InvalidRequestError.sub_code_match(code):
                fields = error["fields"]
                for field in fields:
                    if field in form:
                        form[field].errors += fields[field]
            elif errors.UserAlreadyExistsError.sub_code_match(code):
                message = "User already exists."
            else:
                message = "Internal error. Try again."

            return render_template("register.html", title=title, form=form, message=message)

        return redirect(url_for("users.login"))

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

        if response.status_code != 200:
            error = response.json()["error"]
            code = error["code"]

            message = ""
            if errors.InvalidRequestError.sub_code_match(code):
                fields = error["fields"]
                for field in fields:
                    if field in form:
                        form[field].errors += fields[field]
            elif errors.UserNotFoundError.sub_code_match(code):
                message = "User not found."
            elif errors.WrongCredentialsError.sub_code_match(code):
                message = "Wrong password."
            else:
                message = "Internal error. Try again."

            return render_template("login.html", title=title, form=form, message=message)

        resp = make_response(redirect("/"))
        access_token, refresh_token = (response.json()[field] for field in ("access_token", "refresh_token"))
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp

    return render_template("login.html", title=title, form=form)


@blueprint.route("/logout", methods=["GET"])
def logout():
    resp = redirect("/")
    unset_jwt_cookies(resp)
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
    return render_template("user_info.html", title=f"User information", user=data)


@blueprint.route("/user/<username>/edit_profile", methods=['GET', 'POST'])
@jwt_required()
def edit_user_profile(username):
    if current_user.username != username and not ModeratorGroup.is_belong(current_user.group):
        return redirect(url_for("users.edit_user_profile", username=current_user.username))

    title = "Edit profile"

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
        if response.status_code != 200:
            error = response.json()["error"]
            code = error["code"]

            message = ""
            if errors.InvalidRequestError.sub_code_match(code):
                fields = error["fields"]
                for field in fields:
                    if field in form:
                        form[field].errors += fields[field]
            elif errors.UserNotFoundError.sub_code_match(code):
                message = "User not found"
            else:
                message = "Internal error. Try again."

            return render_template("user_profile_edit.html", title=title, message=message, **template_vars)

        return redirect(url_for("users.edit_user_profile", username=form.username.data))

    user_data = ApiGet.make_request("users", username).json()
    if "user" not in user_data:
        return redirect("/")
    user_data = user_data["user"]
    form.username.data = user_data["username"]
    if user_data["bio"]:
        form.bio.data = user_data["bio"]

    return render_template("user_profile_edit.html", title=title, **template_vars)
