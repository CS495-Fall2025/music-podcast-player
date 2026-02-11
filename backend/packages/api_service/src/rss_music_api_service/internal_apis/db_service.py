from urllib.parse import urljoin

from flask import current_app
import requests

from rss_music_db_service_schemas import ErrorResponse, ErrorType
from rss_music_db_service_schemas.users import (
    requests as db_requests,
    responses as db_responses,
)

from rss_music_api_service.internal_apis import errors
from rss_music_api_service.logging_config import log_request, get_logger


TIMEOUT = (2, 5) # 2 Seconds to connect, 5 seconds to recieve response.
logger = get_logger(__name__)


def create_user(username: str, email: str, password: str) -> None:
    request = _create_user_request(username, email, password)

    response = _send_request(request)

    if not response.status_code == 201:
        _handle_error(response)


def check_user_exists(id: int) -> bool:
    request = _create_user_exists_request(id)

    response = _send_request(request)

    if not response.status_code == 200:
        _handle_error(response)

    response_data = db_responses.UserExistsResponse().load(response.json())

    return response_data["exists"]


# Returns user_id, username on success, None for invalid credentials.
def try_user_login(username: str, password: str) -> tuple[int, str] | None:
    request = _create_user_login_request(username, password)

    response = _send_request(request)

    if response.status_code == 401:
        return

    if not response.status_code == 200:
        _handle_error(response)

    response_data = db_responses.UserLoginResponse().load(response.json())

    return response_data["id"], response_data["username"]


def _create_user_request(username: str, email: str, password: str) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, "users/create")

    request_data = db_requests.CreateUserRequest().dump({
        "username": username,
        "email": email,
        "password": password,
    })
    request = requests.Request("POST", url, json=request_data)

    return request.prepare()


def _handle_error(response: requests.Response) -> None:
    error_data = ErrorResponse().load(response.json())

    match error_data["error"]:
        case ErrorType.INVALID_FORMAT:
            raise errors.InternalAPIBadRequestError(
                "Recieved InvalidFormat from database service"
            )
        case ErrorType.INVALID_ARGUMENT:
            raise errors.InternalAPIBadRequestError(
                "Recieved InvalidArgument from database service"
            )
        case ErrorType.NOT_UNIQUE:
            raise errors.InternalAPIUniquenessError(
                "At least one field was not unique",
                error_data["details"]["field"],
            )
        case _:
            raise errors.InternalAPIReturnedError(
                error_data["message"],
            )


def _create_user_exists_request(id: int) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, "users/exists")

    request_data = db_requests.UserExistsRequest().dump({
        "id": id,
    })
    request = requests.Request("POST", url, json=request_data)

    return request.prepare()


def _create_user_login_request(username: str, password: str) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, "users/login")

    request_data = db_requests.UserLoginRequest().dump({
        "username": username,
        "password": password,
    })
    request = requests.Request("POST", url, json=request_data)

    return request.prepare()


def _send_request(request: requests.PreparedRequest) -> requests.Response:
    log_request(
        logger,
        "info",
        "internal_request_sent",
        "Request sent to DB service",
        service="DBService",
        url=request.url,
        method=request.method,
    )
    
    with requests.Session() as session:
        try:
            response = session.send(request, timeout=TIMEOUT)
            
            level = "info" if response.status_code < 400 else "warn" if response.status_code < 500 else "error"
            log_request(
                logger,
                level,
                "internal_response_received",
                "Response received from DB service",
                service="DBService",
                status_code=response.status_code,
            )
            
            return response
        except requests.Timeout:
            log_request(
                logger,
                "error",
                "internal_timeout",
                "DB service timeout",
                service="DBService",
            )
            raise errors.InternalAPITimeoutError("DBService")
        except requests.RequestException as e:
            log_request(
                logger,
                "error",
                "internal_error",
                "Error communicating with DB service",
                service="DBService",
                error=str(e),
            )
            raise errors.InternalAPITransportError(
                "An error occurred while sending a request to the database service"
            )
