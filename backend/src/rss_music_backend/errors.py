from enum import Enum, auto


class RequestError(Enum):
    INVALID_FORMAT = auto()
    INVALID_ARGUMENT = auto()
    EXTERNAL_API_UNAVALIABLE = auto()


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
}


def get_error_response(error: RequestError) -> dict[str, str]:
    json_response = _ERROR_RESPONSE_VALUES[error]
    return json_response, json_response["code"]
