from unittest import mock
import hashlib
import base64

import pytest
from requests import exceptions, PreparedRequest, Response

from tests.integration.api_mocks import db_service_mock

SEND_METHOD = "requests.Session.send"
ENDPOINT_URL = "/auth/login"


@pytest.fixture
def test_user():
    """Create a test user for login tests."""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "password": "Password123!",
        "user_id": 0,
    }


def generate_code_verifier():
    return (
        base64.urlsafe_b64encode(b"test_verifier_string_12345678901234567890")
        .decode("utf-8")
        .rstrip("=")
    )


def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


@pytest.fixture
def pkce_challenge(client):
    """Initialize PKCE challenge in session."""
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)

    response = client.get(f"/auth/?code_challenge={challenge}")
    assert response.status_code == 200

    return {"verifier": verifier, "challenge": challenge}


def test_empty_post_returns_invalid_format(client, test_user, pkce_challenge) -> None:
    response = client.post(ENDPOINT_URL)

    assert response.status_code == 400

    data = response.get_json()
    assert 400 == data["code"]
    assert "InvalidFormat" == data["error"]


def test_malformed_post_returns_invalid_format(
    client, test_user, pkce_challenge
) -> None:
    response = client.post(
        ENDPOINT_URL, data="NOT_JSON", content_type="application/json"
    )

    assert response.status_code == 400

    data = response.get_json()
    assert 400 == data["code"]
    assert "InvalidFormat" == data["error"]


def test_missing_username_returns_invalid_argument(
    client, test_user, pkce_challenge
) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "password": test_user["password"],
            "code_verifier": pkce_challenge["verifier"],
        },
    )

    assert response.status_code == 400

    data = response.get_json()
    assert 400 == data["code"]
    assert "InvalidArgument" == data["error"]


def test_missing_password_returns_invalid_argument(
    client, test_user, pkce_challenge
) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": test_user["username"],
            "code_verifier": pkce_challenge["verifier"],
        },
    )

    assert response.status_code == 400

    data = response.get_json()
    assert 400 == data["code"]
    assert "InvalidArgument" == data["error"]


def test_missing_code_verifier_returns_invalid_argument(
    client, test_user, pkce_challenge
) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )

    assert response.status_code == 400

    data = response.get_json()
    assert 400 == data["code"]
    assert "InvalidArgument" == data["error"]


def test_no_pkce_challenge_in_session_returns_error(client, test_user) -> None:
    verifier = generate_code_verifier()

    response = client.post(
        ENDPOINT_URL,
        json={
            "username": test_user["username"],
            "password": test_user["password"],
            "code_verifier": verifier,
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == 400
    assert data["error"] == "InvalidSession"
    assert "PKCE" in data["message"]


def test_invalid_pkce_verifier_returns_error(client, test_user, pkce_challenge) -> None:
    wrong_verifier = generate_code_verifier() + "_wrong"

    response = client.post(
        ENDPOINT_URL,
        json={
            "username": test_user["username"],
            "password": test_user["password"],
            "code_verifier": wrong_verifier,
        },
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data["code"] == 401
    assert data["error"] == "InvalidPKCE"
    assert "PKCE" in data["message"]


def test_invalid_credentials_returns_error(client, test_user, pkce_challenge) -> None:
    def generate_failed_login(request: PreparedRequest, *args, **kwargs) -> Response:
        return db_service_mock.generate_users_login_failure(request)

    with mock.patch(SEND_METHOD, side_effect=generate_failed_login) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": "nonexistent_user",
                "password": test_user["password"],
                "code_verifier": pkce_challenge["verifier"],
            },
        )

    assert response.status_code == 401
    data = response.get_json()
    assert data["code"] == 401
    assert data["error"] == "InvalidCredentials"
    assert "credentials" in data["message"].lower()


def test_successful_login_returns_cookies(client, test_user, pkce_challenge) -> None:
    def generate_successful_login(
        request: PreparedRequest, *args, **kwargs
    ) -> Response:
        return db_service_mock.generate_users_login_success(
            request, test_user["user_id"]
        )

    with mock.patch(SEND_METHOD, side_effect=generate_successful_login) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": test_user["username"],
                "password": test_user["password"],
                "code_verifier": pkce_challenge["verifier"],
            },
        )

    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True

    # Check that cookies were set
    cookies = {}
    for header in response.headers.getlist("Set-Cookie"):
        if "access_token=" in header:
            cookies["access_token"] = header
        elif "refresh_token=" in header:
            cookies["refresh_token"] = header

    # Verify both cookies exist and have values
    assert "access_token" in cookies
    assert "refresh_token" in cookies
    assert "access_token=;" not in cookies["access_token"]  # not empty
    assert "refresh_token=;" not in cookies["refresh_token"]  # not empty
    assert "Max-Age=3600" in cookies["access_token"]
    assert "Max-Age=604800" in cookies["refresh_token"]


def test_unverified_email_cannot_login(client, test_user, pkce_challenge) -> None:
    def generate_unverified_login(
        request: PreparedRequest, *args, **kwargs
    ) -> Response:
        return db_service_mock.generate_users_login_success(
            request, test_user["user_id"], email_verified=False
        )

    with mock.patch(SEND_METHOD, side_effect=generate_unverified_login) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": test_user["username"],
                "password": test_user["password"],
                "code_verifier": pkce_challenge["verifier"],
            },
        )

    assert response.status_code == 403
    data = response.get_json()
    assert data["error"] == "EmailNotVerified"


def test_successful_login_clears_pkce_from_session(
    client, test_user, pkce_challenge
) -> None:
    def generate_successful_login(
        request: PreparedRequest, *args, **kwargs
    ) -> Response:
        return db_service_mock.generate_users_login_success(
            request, test_user["user_id"]
        )

    with mock.patch(SEND_METHOD, side_effect=generate_successful_login) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": test_user["username"],
                "password": test_user["password"],
                "code_verifier": pkce_challenge["verifier"],
            },
        )

    assert response.status_code == 200

    response2 = client.post(
        ENDPOINT_URL,
        json={
            "username": test_user["username"],
            "password": test_user["password"],
            "code_verifier": pkce_challenge["verifier"],
        },
    )

    assert response2.status_code == 400
    data = response2.get_json()
    assert data["error"] == "InvalidSession"
    assert "PKCE" in data["message"]


def test_login_returns_bad_request(client, test_user, pkce_challenge) -> None:
    def generate_invalid_format(request: PreparedRequest, *args, **kwargs) -> Response:
        return db_service_mock.generate_invalid_format(request)

    with mock.patch(SEND_METHOD, side_effect=generate_invalid_format) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": test_user["username"],
                "password": test_user["password"],
                "code_verifier": pkce_challenge["verifier"],
            },
        )

    assert response.status_code == 502

    data = response.get_json()

    assert 502 == data["code"]
    assert "InternalApiBadResponse" == data["error"]


def test_login_returns_timeout(client, test_user, pkce_challenge) -> None:
    def generate_timeout(request: PreparedRequest, *args, **kwargs) -> Response:
        raise exceptions.Timeout()

    with mock.patch(SEND_METHOD, side_effect=generate_timeout) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": test_user["username"],
                "password": test_user["password"],
                "code_verifier": pkce_challenge["verifier"],
            },
        )

    assert response.status_code == 504

    data = response.get_json()

    assert 504 == data["code"]
    assert "InternalApiTimeout" == data["error"]
