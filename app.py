# -*- coding: utf-8 -*-

from configparser import ConfigParser

from flask import Flask, redirect, make_response
from flask_jwt_extended import JWTManager, current_user, unset_jwt_cookies, unset_access_cookies

from data import db_session
from data import users_api
from data.api_errors import AppError
from data.users import User
from views import default as default_blueprint
from views import users as users_blueprint

config = ConfigParser()
config.read("config.ini", encoding="utf-8")

app = Flask(__name__)
app.config["SECRET_KEY"] = config["App"]["SecretKey"]
app.config["JWT_SECRET_KEY"] = config["App"]["JWTSecretKey"]
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config['JWT_TOKEN_LOCATION'] = ["cookies"]
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_CSRF_CHECK_FORM'] = True

jwt = JWTManager(app)


@app.context_processor
def inject_current_user():
    return dict(current_user=current_user)


@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return user_id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    user_id = jwt_data["sub"]
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.errorhandler(AppError)
def app_errors_handler(error):
    return error.create_response()


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
    app.register_blueprint(default_blueprint.blueprint)
    app.register_blueprint(users_blueprint.blueprint)

    # API
    app.register_blueprint(users_api.blueprint)

    app.run()


if __name__ == "__main__":
    main()
