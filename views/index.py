from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

blueprint = Blueprint(
    "default_blueprint",
    __name__,
)


@blueprint.route("/")
@jwt_required(optional=True)
def index():
    return render_template("index.html", title="Quick Polls")
