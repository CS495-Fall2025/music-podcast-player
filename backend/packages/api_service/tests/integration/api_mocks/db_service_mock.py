import json

from requests import PreparedRequest, Response

from rss_music_db_service_schemas import ErrorResponse, ErrorType
from rss_music_db_service_schemas.users import (
    requests as db_requests,
    responses as db_responses,
)


def generate_invalid_format(_request: PreparedRequest) -> Response:
    sdata = ErrorResponse().dumps(
        {
            "error": ErrorType.INVALID_FORMAT,
            "message": "Expected a JSON body",
        }
    )

    response = Response()
    response.status_code = 400
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response


def generate_invalid_argument(_request: PreparedRequest) -> Response:
    sdata = ErrorResponse().dumps(
        {
            "error": ErrorType.INVALID_ARGUMENT,
            "message": "Request did not match expected schema",
            "details": {
                "fieldname": ["Expected something cooler"],
            },
        }
    )

    response = Response()
    response.status_code = 400
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response


def generate_users_create_success(request: PreparedRequest) -> Response:
    body = json.loads(request.body.decode("UTF-8"))
    request_data = db_requests.CreateUserRequest().load(body)

    sdata = db_responses.CreateUserResponse().dumps(
        {
            "username": request_data["username"],
        }
    )

    response = Response()
    response.status_code = 201
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response


def generate_users_create_not_unique(_request: PreparedRequest, field: str) -> Response:
    sdata = ErrorResponse().dumps(
        {
            "error": ErrorType.NOT_UNIQUE,
            "message": "The username or email has been used already",
            "details": {
                "field": field,
            },
        }
    )

    response = Response()
    response.status_code = 409
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response


def generate_users_exists(_request: PreparedRequest, exists: bool) -> Response:
    sdata = db_responses.UserExistsResponse().dumps(
        {
            "exists": exists,
        }
    )

    response = Response()
    response.status_code = 200
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response


def generate_users_login_success(
    request: PreparedRequest, id: int, email_verified: bool = True
) -> Response:
    body = json.loads(request.body.decode("UTF-8"))
    request_data = db_requests.UserLoginRequest().load(body)

    sdata = db_responses.UserLoginResponse().dumps(
        {
            "username": request_data["username"],
            "id": id,
            "email_verified": email_verified,
        }
    )

    response = Response()
    response.status_code = 200
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response


def generate_users_login_failure(_request: PreparedRequest) -> Response:
    sdata = ErrorResponse().dumps(
        {
            "error": ErrorType.INVALID_CREDENTIALS,
            "message": "The provided credentials are invalid",
        }
    )

    response = Response()
    response.status_code = 401
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response


def generate_operation_success(success: bool) -> Response:
    sdata = json.dumps({"success": success})

    response = Response()
    response.status_code = 200
    response._content = sdata.encode("UTF-8")
    response.headers = {"Content-Type": "application/json"}

    return response
