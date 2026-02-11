from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from rss_music_api_service.errors import RequestError, get_error_response
from rss_music_api_service.external_apis.concrete import LinkFunctions
from rss_music_api_service.external_apis.errors import ExternalAPIError, ExternalAPITransportError
from rss_music_api_service.schemas import LinkFeedRequestSchema

LINK_BP = Blueprint("link", __name__, url_prefix="/link")


@LINK_BP.get("/feed")
def get_link_feed() -> dict:
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
    except ExternalAPITransportError:
        return get_error_response(RequestError.EXTERNAL_API_TIMEOUT)
    except ExternalAPIError:
        return get_error_response(RequestError.EXTERNAL_API_BAD_RESPONSE)

    return {
        "code": 200,
        "feed": feed,
    }
