from enum import Enum, auto


class RequestError(Enum):
    INVALID_FORMAT = auto()
    INVALID_ARGUMENT = auto()
    EXTERNAL_API_TIMEOUT = auto()
    EXTERNAL_API_BAD_RESPONSE = auto()
    VALUE_NOT_UNIQUE = auto()
    INTERNAL_API_TIMEOUT = auto()
    INTERNAL_API_BAD_RESPONSE = auto()


_ERROR_RESPONSE_VALUES = {
    RequestError.INVALID_FORMAT: {
        "error": "InvalidFormat",
        "message": "Malformed JSON in request",
        "code": 400,
    },
    RequestError.INVALID_ARGUMENT: {
        "error": "InvalidArgument",
        "message": "Arguments did not match expected schema",
        "code": 400,
    },
    RequestError.VALUE_NOT_UNIQUE: {
        "error": "ValueNotUnique",
        "message": "This {field} is already in use",
        "field": "unknown",
        "code": 409,
    },
    RequestError.INTERNAL_API_TIMEOUT: {
        "error": "InternalApiTimeout",
        "message": ("We were unable to reach the internal API we use for this request"),
        "code": 504,
    },
    RequestError.INTERNAL_API_BAD_RESPONSE: {
        "error": "InternalApiBadResponse",
        "message": (
            "The response from the internal API we use for this request was invalid"
        ),
        "code": 502,
    },
    RequestError.EXTERNAL_API_TIMEOUT: {
        "error": "ExternalApiTimeout",
        "message": ("We were unable to reach the external API we use for this request"),
        "code": 504,
    },
    RequestError.EXTERNAL_API_BAD_RESPONSE: {
        "error": "ExternalApiBadResponse",
        "message": (
            "The response from the external API we use for this request was invalid"
        ),
        "code": 502,
    },
}


def get_error_response(
    error: RequestError, modified_args: dict | None = None
) -> tuple[dict[str, str], int]:
    json_response = _ERROR_RESPONSE_VALUES[error].copy()

    if modified_args is not None:
        for key, value in modified_args.items():
            json_response[key] = value

        if "field" in json_response and "{field}" in json_response["message"]:
            json_response["message"] = json_response["message"].replace(
                "{field}", json_response["field"]
            )

    status_code = json_response["code"]
    return json_response, status_code
