from urllib.parse import urljoin

from flask import current_app
import requests
from marshmallow import exceptions

from rss_music_db_service_schemas import ErrorResponse, ErrorType
from rss_music_db_service_schemas.users import (
    requests as db_requests,
    responses as db_responses,
)

from rss_music_db_service_schemas.playlists import (
    requests as playlist_requests,
    responses as playlist_responses,
)

from rss_music_api_service.internal_apis import auth, errors
from rss_music_api_service.logging_config import log_request, get_logger

TIMEOUT = (5, 10)  # 2 Seconds to connect, 5 seconds to recieve response.

logger = get_logger(__name__)

# Users


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


# Returns user_id, username, email_verified on success, None for invalid credentials.
def try_user_login(username: str, password: str) -> tuple[int, str, bool] | None:
    request = _create_user_login_request(username, password)

    response = _send_request(request)

    if response.status_code == 401:
        return

    if not response.status_code == 200:
        _handle_error(response)

    response_data = db_responses.UserLoginResponse().load(response.json())

    return (
        response_data["id"],
        response_data["username"],
        response_data["email_verified"],
    )


def set_email_verification_code(email: str, code: str, expires_at: str) -> bool:
    request = _create_set_email_verification_code_request(email, code, expires_at)

    response = _send_request(request)

    if response.status_code != 200:
        _handle_error(response)

    return bool(response.json().get("success", False))


def verify_email(email: str, code: str) -> bool:
    request = _create_verify_email_request(email, code)

    response = _send_request(request)

    if response.status_code != 200:
        _handle_error(response)

    return bool(response.json().get("success", False))


def set_password_reset_code(email: str, code: str, expires_at: str) -> bool:
    request = _create_set_password_reset_code_request(email, code, expires_at)

    response = _send_request(request)

    if response.status_code != 200:
        _handle_error(response)

    return bool(response.json().get("success", False))


def reset_password(email: str, code: str, new_password: str) -> bool:
    request = _create_reset_password_request(email, code, new_password)

    response = _send_request(request)

    if response.status_code != 200:
        _handle_error(response)

    return bool(response.json().get("success", False))


def _create_user_request(
    username: str, email: str, password: str
) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, "users/create")

    request_data = db_requests.CreateUserRequest().dump(
        {
            "username": username,
            "email": email,
            "password": password,
        }
    )
    request = requests.Request("POST", url, json=request_data)

    return request.prepare()


def _handle_error(response: requests.Response) -> None:
    try:
        error_data = ErrorResponse().load(response.json())
    except exceptions.ValidationError as error:
        raise errors.InternalAPIBadResponseError(
            "Recieved unexpected data from database service",
            error.messages,
        )

    match error_data["error"]:
        case ErrorType.INVALID_FORMAT:
            raise errors.InternalAPIBadResponseError(
                "Recieved InvalidFormat from database service"
            )
        case ErrorType.INVALID_ARGUMENT:
            raise errors.InternalAPIBadResponseError(
                "Recieved InvalidArgument from database service"
            )
        case ErrorType.NOT_UNIQUE:
            raise errors.InternalAPIUniquenessError(
                "At least one field was not unique",
                error_data["details"]["field"],
            )
        case ErrorType.NOT_FOUND:
            raise errors.InternalAPINotFoundError(error_data["message"])
        case _:
            raise errors.InternalAPIReturnedError(
                error_data["message"],
            )


def _create_user_exists_request(id: int) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, "users/exists")

    request_data = db_requests.UserExistsRequest().dump(
        {
            "id": id,
        }
    )
    request = requests.Request("POST", url, json=request_data)

    return request.prepare()


def _create_user_login_request(
    username: str, password: str
) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, "users/login")

    request_data = db_requests.UserLoginRequest().dump(
        {
            "username": username,
            "password": password,
        }
    )
    request = requests.Request("POST", url, json=request_data)

    return request.prepare()


def _create_set_email_verification_code_request(
    email: str, code: str, expires_at: str
) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, "users/set-email-verification-code")

    request_data = {
        "email": email,
        "code": code,
        "expires_at": expires_at,
    }
    request = requests.Request("POST", url, json=request_data)

    return request.prepare()


def _create_verify_email_request(email: str, code: str) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, "users/verify-email")

    request_data = {
        "email": email,
        "code": code,
    }
    request = requests.Request("POST", url, json=request_data)

    return request.prepare()


def _create_set_password_reset_code_request(
    email: str, code: str, expires_at: str
) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, "users/set-password-reset-code")

    request_data = {
        "email": email,
        "code": code,
        "expires_at": expires_at,
    }
    request = requests.Request("POST", url, json=request_data)

    return request.prepare()


def _create_reset_password_request(
    email: str, code: str, new_password: str
) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, "users/reset-password")

    request_data = {
        "email": email,
        "code": code,
        "new_password": new_password,
    }
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
        auth_obj = auth.get_auth()
        try:
            if auth_obj is not None:
                request = auth_obj(request)
            response = session.send(request, timeout=TIMEOUT)

            level = (
                "info"
                if response.status_code < 400
                else "warn"
                if response.status_code < 500
                else "error"
            )
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


# Playlists


def create_playlist(title: str, user_id: int, description: str = None) -> dict:
    # Prepare  internal request
    request = _create_playlist_request(title, user_id, description)

    # Send it to DB Service
    response = _send_request(request)

    # Handle errors
    if not response.status_code == 201:
        _handle_error(response)

    return response.json()


def _create_playlist_request(
    title: str, user_id: int, description: str
) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]

    # Matches the endpoint the DB service expects
    url = urljoin(service_url, "playlists/create")

    data_to_dump = {
        "title": title,
        "created_by_user_id": user_id,
    }

    if description is not None:
        data_to_dump["description"] = description

    # Use Schema to 'dump' data into a clean dictionary
    request_data = playlist_requests.CreatePlaylistRequest().dump(data_to_dump)

    request = requests.Request("POST", url, json=request_data)
    return request.prepare()


def get_user_playlists(user_id: int) -> list[dict]:
    # Prepare GET request
    request = _create_get_user_playlists_request(user_id)

    # Send request
    response = _send_request(request)

    # Error handling
    if not response.status_code == 200:
        _handle_error(response)

    return response.json()


def _create_get_user_playlists_request(user_id: int) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]

    # Build URL
    url = urljoin(service_url, f"playlists/user/{user_id}")

    request = requests.Request("GET", url)
    return request.prepare()


def update_playlist(
    playlist_id: int, user_id: int, title: str = None, description: str = None
) -> dict:
    # Prepare request
    request = _create_update_playlist_request(playlist_id, user_id, title, description)

    # Send request
    response = _send_request(request)

    # Error handling
    if not response.status_code == 200:
        _handle_error(response)

    raw_data = response.json()

    validated_data = playlist_responses.UpdatePlaylistResponse().load(raw_data)

    # Return newly updated playlist
    return validated_data


def _create_update_playlist_request(
    playlist_id, user_id, title, description
) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, f"playlists/{playlist_id}")

    request_data = {"created_by_user_id": user_id}

    if title is not None:
        request_data |= {"title": title}
    if description is not None:
        request_data |= {"description": description}

    request_data = playlist_requests.UpdatePlaylistRequest().dump(request_data)

    request = requests.Request("PUT", url, json=request_data)
    return request.prepare()


def delete_playlist(playlist_id: int, user_id: int) -> None:
    # Create request
    request = _create_delete_playlist_request(playlist_id, user_id)

    # Send request
    response = _send_request(request)

    # Error handling
    if not response.status_code == 200:
        _handle_error(response)


def _create_delete_playlist_request(playlist_id, user_id) -> requests.PreparedRequest:
    service_url = current_app.config["DB_SERVICE_URL"]
    url = urljoin(service_url, f"playlists/{playlist_id}")

    request_data = {"created_by_user_id": user_id}
    request = requests.Request("DELETE", url, json=request_data)
    return request.prepare()
