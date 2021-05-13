import os

from flask import redirect, make_response, url_for, flash, request
from flask_babel import _
from flask_jwt_extended import current_user, unset_jwt_cookies, unset_access_cookies, jwt_required

from qp import babel, jwt, app
from qp.api.database import db_session
from qp.api.models.users import groups, get_group, User
from qp.tools.languages import LANGUAGES, GROUPS
from qp.tools.moment import MomentJs


@babel.localeselector
def get_locale():
    """Getting current language"""
    language = request.cookies.get("language")
    if language not in LANGUAGES.keys():
        return request.accept_languages.best_match(LANGUAGES.keys())
    return language


@app.before_request
@jwt_required(optional=True)
def logout_if_banned():
    """Logout if current user is banned"""
    if request.path.startswith("/api"):
        return
    if current_user and current_user.banned:
        resp = make_response(redirect("/"))
        unset_jwt_cookies(resp)
        flash(_("You were banned."), "danger")
        return resp


@app.context_processor
def inject_template_variables():
    """Adding variables to Jinja2 engine"""
    groups_dict = {group.title: group for group in groups}
    return dict(current_user=current_user,
                groups=groups_dict,
                groups_translations=GROUPS,
                get_group=get_group,
                moment=MomentJs,
                langs=LANGUAGES)


@app.template_filter("get_avatar")
def get_avatar(filename):
    """Get user avatar"""
    path = url_for("static", filename="avatars")
    extension = ".png"
    files = os.listdir("qp/" + path[1:])
    if type(filename) is not str or filename + extension not in files:
        filename = "default"
    return path + "/" + filename + extension


@jwt.user_identity_loader
def user_identity_lookup(user_id):
    """Getting JWT identity"""
    return user_id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Getting current_user from database"""
    user_id = jwt_data["sub"]
    session = db_session.create_session()
    return session.query(User).get(user_id)


@jwt.unauthorized_loader
def unauthorized_callback(*args):
    """Log in if user is unauthorized, but authorization is required"""
    return redirect("/login")


@jwt.invalid_token_loader
def invalid_token_callback(*args):
    """Remove cookies and log in if JWT tokens are invalid"""
    response = make_response(redirect("/login"))
    unset_jwt_cookies(response)
    return response


@jwt.expired_token_loader
def expired_token_callback(*args):
    """Update token if expired"""
    response = make_response(redirect("/token/refresh"))
    unset_access_cookies(response)
    return response


@jwt.user_lookup_error_loader
def user_lookup_callback(*args):
    """Log in if current_user not found"""
    response = make_response(redirect("/login"))
    unset_jwt_cookies(response)
    return response
