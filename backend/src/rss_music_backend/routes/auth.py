from flask import Blueprint, request
from marshmallow import ValidationError

from rss_music_backend.errors import RequestError, get_error_response
from rss_music_backend.schemas import SignUpRequestSchema

# All routes added to this BP are under "/math", so "" would just be "/math".
SEARCH_BP = Blueprint("auth", __name__, url_prefix="/auth")


@SEARCH_BP.post("/signup")
def post_signup() -> dict:
    try:
        data = request.get_json(silent=True)

        if data == None:
            return get_error_response(RequestError.INVALID_FORMAT)

        valid_request = SignUpRequestSchema().load(data)

    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    return {
        "code": 201,
    }
