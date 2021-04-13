# -*- coding: utf-8 -*-

from configparser import ConfigParser
import os

from flask import Flask, redirect, make_response, url_for
from flask_jwt_extended import JWTManager, current_user, unset_jwt_cookies, unset_access_cookies

from api.database import db_session
from api.handlers import polls, users, errors
from api.models.users import User, groups
from tools.users import get_avatar
import views.index
import views.users
import views.polls

config = ConfigParser()
config.read("config.ini", encoding="utf-8")

app = Flask(__name__)
app.config["SECRET_KEY"] = config["App"]["SecretKey"]
app.config["JWT_SECRET_KEY"] = config["App"]["JWTSecretKey"]
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # CHANGE IN PROD
app.config["JWT_CSRF_CHECK_FORM"] = False  # CHANGE IN PROD
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # DELETE IN PROD

jwt = JWTManager(app)


@app.context_processor
def inject_current_user():
    groups_dict = {group.title: group for group in groups}
    return dict(current_user=current_user, groups=groups_dict)


@app.template_filter("get_avatar")
def get_avatar(filename):
    path = url_for("static", filename="avatars")
    extension = ".png"
    files = os.listdir(path[1:])
    if type(filename) is not str or filename + extension not in files:
        filename = "default"
    return path + "/" + filename + extension


@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return user_id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    user_id = jwt_data["sub"]
    session = db_session.create_session()
    return session.query(User).get(user_id)


@jwt.unauthorized_loader
def unauthorized_callback(*args):
    return redirect("/login")


@jwt.invalid_token_loader
def invalid_token_callback(*args):
    response = make_response(redirect("/login"))
    unset_jwt_cookies(response)
    return response


@jwt.expired_token_loader
def expired_token_callback(*args):
    response = make_response(redirect("/token/refresh"))
    unset_access_cookies(response)
    return response


@jwt.user_lookup_error_loader
def user_lookup_callback(*args):
    response = make_response(redirect("/login"))
    unset_jwt_cookies(response)
    return response


def main():
    db_session.global_init("db/app.db")

    # Blueprints
    app.register_blueprint(views.index.blueprint)
    app.register_blueprint(views.users.blueprint)
    app.register_blueprint(views.polls.blueprint)

    # API
    api_url_prefix = "/api"
    app.register_blueprint(errors.blueprint)
    app.register_blueprint(users.blueprint, url_prefix=api_url_prefix)
    app.register_blueprint(polls.blueprint, url_prefix=api_url_prefix)

    app.run()


if __name__ == "__main__":
    main()
