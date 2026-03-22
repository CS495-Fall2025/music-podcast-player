from flask import Blueprint, request, g
from marshmallow import ValidationError

from rss_music_api_service.errors import RequestError, get_error_response
from rss_music_api_service.external_apis.concrete import PodcastIndexAPI
from rss_music_api_service.external_apis.errors import (
    ExternalAPIReturnedError,
    ExternalAPIResponseError,
    ExternalAPITransportError,
)
from rss_music_api_service.schemas import SearchFeedsRequestSchema

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
    except ValidationError as error:
        g.details = {
            "error": "InvalidArgument",
            "validation_messages": error.messages,
        }
        return get_error_response(RequestError.INVALID_ARGUMENT)
    except ExternalAPITransportError:
        g.details = {
            "error": "ExternalApiTimeout",
            "api": "PodcastIndex",
        }
        return get_error_response(RequestError.EXTERNAL_API_TIMEOUT)
    except ExternalAPIReturnedError as error:
        g.details = {
            "error": "ExternalApiReturnedError",
            "api": "PodcastIndex",
            "message": str(error),
        }
        return get_error_response(RequestError.EXTERNAL_API_BAD_RESPONSE)
    except ExternalAPIResponseError as error:
        g.details = {
            "error": "ExternalApiResponseError",
            "message": str(error),
        }
        return get_error_response(RequestError.EXTERNAL_API_BAD_RESPONSE)

    return {
        "code": 200,
        "feeds": feeds,
    }
