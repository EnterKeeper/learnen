from flask import Blueprint
from flask_restful import Api

blueprint = Blueprint(
    "polls_resource",
    __name__,
)
api = Api(blueprint)
