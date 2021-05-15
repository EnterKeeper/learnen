# -*- coding: utf-8 -*-

from flask import Flask
from flask_babel import Babel
from flask_jwt_extended import JWTManager
from flask_mail import Mail

from qp.api.database import db_session
from qp.api.tools.database import create_owner_user
from .config import Config

app = Flask(__name__)
jwt = JWTManager()
babel = Babel()
mail = Mail()


def create_app():
    """App creation"""
    app.config.from_object(Config)

    db_session.global_init("qp/db/app.db")
    create_owner_user()

    jwt.init_app(app)
    babel.init_app(app)
    mail.init_app(app)

    from qp.tools import settings

    from qp.views import default
    from qp.views import users
    from qp.views import polls

    from qp.api.handlers import errors as api_errors
    from qp.api.handlers import users as api_users
    from qp.api.handlers import polls as api_polls

    # Registering views blueprints
    app.register_blueprint(default.blueprint)
    app.register_blueprint(users.blueprint)
    app.register_blueprint(polls.blueprint)

    # Registering API blueprints
    api_url_prefix = "/api"
    app.register_blueprint(api_errors.blueprint)
    app.register_blueprint(api_users.blueprint, url_prefix=api_url_prefix)
    app.register_blueprint(api_polls.blueprint, url_prefix=api_url_prefix)

    return app
