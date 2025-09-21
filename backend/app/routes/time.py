from flask import Blueprint, request


time_blueprint = Blueprint("time", __name__)


@time_blueprint.get("/time")
def get_time() -> dict:
    return {"test": "test"}


@time_blueprint.post("/time")
def post_time() -> dict:
    return {}
