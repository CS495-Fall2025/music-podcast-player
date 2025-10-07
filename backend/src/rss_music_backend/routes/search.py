from flask import Blueprint, request
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest

from rss_music_backend.errors import RequestError, get_error_response
from rss_music_backend.schemas import SearchFeedsRequestSchema

# All routes added to this BP are under "/math", so "" would just be "/math".
SEARCH_BP = Blueprint("search", __name__, url_prefix="/search")


@SEARCH_BP.get("/feeds")
def post_math() -> dict:
    try:
        data = request.get_json()
        validated_request = SearchFeedsRequestSchema().load(data)
    except BadRequest:
        return get_error_response(RequestError.INVALID_FORMAT)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)


