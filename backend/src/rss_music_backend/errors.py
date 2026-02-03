from enum import Enum, auto


class RequestError(Enum):
    INVALID_FORMAT = auto()
    INVALID_ARGUMENT = auto()
    EXTERNAL_API_UNAVALIABLE = auto()
    VALUE_NOT_UNIQUE = auto()


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
    RequestError.EXTERNAL_API_UNAVALIABLE: {
        "error": "ExternalApiUnavaliable",
        "message": (
            "The external API we use to process this request is currently unavaliable"
        ),
        "code": 503,
    },
    RequestError.VALUE_NOT_UNIQUE: {
        "error": "ValueNotUnique",
        "message": "This {field} is already in use",
        "field": "unknown",
        "code": 403,
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
