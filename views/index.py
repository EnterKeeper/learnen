from flask import Blueprint, render_template
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required, current_user


blueprint = Blueprint(
    "default_blueprint",
    __name__,
)


@blueprint.route("/")
@jwt_required(optional=True)
def index():
    return render_template("index.html", title="Welcome!")
