from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from rss_music_api_service.errors import RequestError, get_error_response
from rss_music_api_service.external_apis.concrete import LinkFunctions
from rss_music_api_service.external_apis.errors import ExternalAPIError
from rss_music_api_service.schemas import LinkFeedRequestSchema
from rss_music_api_service.logging_config import log_request, get_logger

LINK_BP = Blueprint("link", __name__, url_prefix="/link")
logger = get_logger(__name__)


@LINK_BP.after_request
def log_response(response):
    level = "info" if response.status_code < 400 else "warn" if response.status_code < 500 else "error"
    log_request(
        logger,
        level,
        "response_sent",
        "Sending response",
        route="/link/feed",
        status_code=response.status_code,
    )
    return response


@LINK_BP.get("/feed")
def get_link_feed() -> dict:
    log_request(
        logger,
        "info",
        "request_received",
        "Link feed request received",
        route="/link/feed",
    )
    
    try:
        data = {"url": request.args.get("url", "")}

        errors = LinkFeedRequestSchema().validate(data)

        if errors:
            return jsonify(
                {
                    "code": 400,
                    "error": "InvalidArgument",
                    "message": "Arguments did not match expected schema",
                    "details": errors,
                }
            ), 400

        validated_request = LinkFeedRequestSchema().load(data)

        feed = LinkFunctions.get_feed_by_url(
            validated_request["url"],
        )

    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)
    except ExternalAPIError:
        return get_error_response(RequestError.EXTERNAL_API_UNAVALIABLE)

    return {
        "code": 200,
        "feed": feed,
    }
