from flask import Blueprint, request
from marshmallow import ValidationError

from rss_music_backend.errors import RequestError, get_error_response
from rss_music_backend.external_apis.concrete import PodcastIndexAPI
from rss_music_backend.external_apis.errors import ExternalAPIError
from rss_music_backend.schemas import SearchFeedsRequestSchema

# All routes added to this BP are under "/math", so "" would just be "/math".
SEARCH_BP = Blueprint("search", __name__, url_prefix="/search")


@SEARCH_BP.get("/feeds")
def get_search_feeds() -> dict:
    try:
        data = request.args
        validated_request = SearchFeedsRequestSchema().load(data)

        feeds = PodcastIndexAPI.search_music_feeds(
            validated_request["query"],
            validated_request["count"],
            validated_request["start"],
        )
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)
    except ExternalAPIError:
        return get_error_response(RequestError.EXTERNAL_API_UNAVALIABLE)

    return {
        "code": 200,
        "feeds": feeds,
    }
