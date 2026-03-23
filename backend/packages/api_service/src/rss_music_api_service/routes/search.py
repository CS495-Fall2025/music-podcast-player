from flask import Blueprint, request, g
from marshmallow import ValidationError

from rss_music_api_service import api_usage
from rss_music_api_service.errors import RequestError, get_error_response
from rss_music_api_service.external_apis.concrete import PodcastIndexAPI
from rss_music_api_service.external_apis.errors import (
    ExternalAPIReturnedError,
    ExternalAPIResponseError,
    ExternalAPITransportError,
    ExternalAPITooManyRequestsError,
)
from rss_music_api_service.schemas import SearchFeedsRequestSchema

SEARCH_BP = Blueprint("search", __name__, url_prefix="/search")


@SEARCH_BP.errorhandler(ExternalAPITransportError)
def handle_transport_error(_error):
    g.details = {
        "error": "ExternalApiTimeout",
        "api": "PodcastIndex",
    }
    return get_error_response(RequestError.EXTERNAL_API_TIMEOUT)


@SEARCH_BP.errorhandler(ExternalAPITooManyRequestsError)
def handle_too_many_requests(_error):
    g.details = {
        "error": "ExternalApiUnavaliable",
        "api": "PodcastIndex",
    }
    api_usage.penalize_user_api_tokens(api_usage.TokenType.PODCAST_INDEX)
    return get_error_response(RequestError.EXTERNAL_API_UNAVALIABLE)


@SEARCH_BP.errorhandler(ExternalAPIReturnedError)
def handle_returned_error(error):
    g.details = {
        "error": "ExternalApiReturnedError",
        "api": "PodcastIndex",
        "message": str(error),
    }
    return get_error_response(RequestError.EXTERNAL_API_BAD_RESPONSE)


@SEARCH_BP.errorhandler(ExternalAPIResponseError)
def handle_response_error(error):
    g.details = {
        "error": "ExternalApiResponseError",
        "api": "PodcastIndex",
        "message": str(error),
    }
    return get_error_response(RequestError.EXTERNAL_API_BAD_RESPONSE)


@SEARCH_BP.get("/feeds")
def get_search_feeds() -> dict:
    data = request.args
    try:
        validated_request = SearchFeedsRequestSchema().load(data)
    except ValidationError as error:
        g.details = {
            "error": "InvalidArgument",
            "validation_messages": error.messages,
        }
        return get_error_response(RequestError.INVALID_ARGUMENT)

    feeds = PodcastIndexAPI.search_music_feeds(
        validated_request["query"],
        validated_request["count"],
        validated_request["start"],
    )

    return {
        "code": 200,
        "feeds": feeds,
    }
