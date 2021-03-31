from flask import Blueprint, render_template, redirect, make_response
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, unset_jwt_cookies

from tools.api import api_post

from forms.user import RegisterForm, LoginForm
from data import api_errors


blueprint = Blueprint(
    "users_blueprint",
    __name__,
)


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    title = "Register"
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", title=title, form=form, message="Passwords dont match")
        user_data = form.data.copy()
        for field in ("password_again", "submit", "csrf_token"):
            user_data.pop(field)
        response = api_post("register", json=user_data)

        if response.status_code != 200:
            error = response.json()["error"]
            code = error["code"]

            message = ""
            if api_errors.InvalidRequestError.sub_code_match(code):
                fields = error["fields"]
                for field in fields:
                    if field in form:
                        form[field].errors += fields[field]
            elif api_errors.UserAlreadyExistsError.sub_code_match(code):
                message = "User already exists."
            else:
                message = "Internal error. Try again."

            return render_template("register.html", title=title, form=form, message=message)

        resp = redirect("/login")
        access_token, refresh_token = (response.json()[field] for field in ("access_token", "refresh_token"))
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return resp

    return render_template("register.html", title=title, form=form)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    title = "Login"
    if form.validate_on_submit():
        user_data = form.data.copy()
        for field in ("submit", "csrf_token"):
            user_data.pop(field)
        response = api_post("login", json=user_data)

        if response.status_code != 200:
            error = response.json()["error"]
            code = error["code"]

            message = ""
            if api_errors.InvalidRequestError.sub_code_match(code):
                fields = error["fields"]
                for field in fields:
                    if field in form:
                        form[field].errors += fields[field]
            elif api_errors.UserNotFoundError.sub_code_match(code):
                message = "User not found."
            elif api_errors.WrongCredentialsError.sub_code_match(code):
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
