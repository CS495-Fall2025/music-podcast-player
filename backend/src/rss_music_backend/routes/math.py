from flask import Blueprint, request
from werkzeug.exceptions import BadRequest

from rss_music_backend.logic import math

# All routes added to this BP are under "/math", so "" would just be "/math".
MATH_BP = Blueprint("math", __name__, url_prefix="/math")


@MATH_BP.get("")
def get_magic_number() -> dict:
    return {"number": 0}


@MATH_BP.post("")
def post_math() -> dict:
    try:
        data = request.get_json()
    except BadRequest:
        return {"error": "invalid_format"}

    # If the request is not a list of integers, return an error response.
    if not isinstance(data, list) or not all(isinstance(e, int) for e in data):
        return {"error": "invalid_argument"}

    sum = math.get_sum(data)
    product = math.get_product(data)

    return {
        "sum": sum,
        "product": product,
    }
