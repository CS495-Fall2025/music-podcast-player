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
from rss_music_api_service.logging_config import log_request, get_logger

SEARCH_BP = Blueprint("search", __name__, url_prefix="/search")
logger = get_logger(__name__)


@SEARCH_BP.after_request
def log_response(response):
    level = (
        "info"
        if response.status_code < 400
        else "warn"
        if response.status_code < 500
        else "error"
    )
    details = {} if not hasattr(g, "details") else g.details
    log_request(
        logger,
        level,
        "response_sent",
        "Sending response",
        route="/search/feeds",
        status_code=response.status_code,
        details=details,
    )
    return response


@SEARCH_BP.get("/feeds")
def get_search_feeds() -> dict:
    log_request(
        logger,
        "info",
        "request_received",
        "Search feeds request received",
        route="/search/feeds",
    )

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
