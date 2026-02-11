from unittest import mock

import pytest
from requests import exceptions, PreparedRequest, Response

from tests.integration.api_mocks import db_service_mock

ENDPOINT_URL = "/auth/signup"
SEND_METHOD = "requests.Session.send"


def test_empty_post_returns_invalid_format(client) -> None:
    response = client.post(ENDPOINT_URL)

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidFormat" == data["error"]


def test_malformed_post_returns_invalid_format(client) -> None:
    response = client.post(
        ENDPOINT_URL, data="NOT_JSON", content_type="application/json"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidFormat" == data["error"]


def test_missing_arg_returns_invalid_argument(client) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "t3st_user57",
            "email": "user@domain.com",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_short_username_returns_invalid_argument(client) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "a" * 3,
            "email": "user@domain.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 400

    data = response.get_json()
    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_long_username_returns_invalid_argument(client) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "a" * 31,
            "email": "user@domain.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_outer_underscore_username_returns_invalid_argument(client) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "_admin",
            "email": "user@domain.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_illegal_characters_username_returns_invalid_argument(client) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "<user>",
            "email": "user@domain.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_invalid_email_returns_invalid_argument(client) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "t3st_user57",
            "email": "domain.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_short_password_returns_invalid_argument(client) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": "@2abcdef",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_long_password_returns_invalid_argument(client) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": "@2" + "a" * 80,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


@pytest.mark.parametrize(
    "password",
    [
        "123456789@%$#!",  # No letter
        "abcdefghijk@%$#!",  # No digit
        "a0b1c2d3e4f5g6h7",  # No special character
    ],
)
def test_weak_password_returns_invalid_argument(client, password) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": password,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


# DB
def test_successful_signup(client) -> None:
    def generate_success(request: PreparedRequest, *args, **kwargs) -> Response:
        return db_service_mock.generate_users_create_success(request)

    with mock.patch(SEND_METHOD, side_effect=generate_success) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

    assert response.status_code == 201

    data = response.get_json()

    assert 201 == data["code"]


def test_duplicate_username_returns_error(client) -> None:
    def generate_duplicate_username(
        request: PreparedRequest, *args, **kwargs
    ) -> Response:
        return db_service_mock.generate_users_create_not_unique(request, "username")

    with mock.patch(SEND_METHOD, side_effect=generate_duplicate_username) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

    assert response.status_code == 409

    data = response.get_json()

    assert 409 == data["code"]
    assert "ValueNotUnique" == data["error"]
    assert "username" == data["field"]
    assert "This username is already in use" == data["message"]


def test_duplicate_email_returns_error(client) -> None:
    def generate_duplicate_email(request: PreparedRequest, *args, **kwargs) -> Response:
        return db_service_mock.generate_users_create_not_unique(request, "email")

    with mock.patch(SEND_METHOD, side_effect=generate_duplicate_email) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

    assert response.status_code == 409

    data = response.get_json()

    assert 409 == data["code"]
    assert "ValueNotUnique" == data["error"]
    assert "email" == data["field"]
    assert "This email is already in use" == data["message"]


def test_reports_when_invalid_format_recieved(client) -> None:
    def generate_invalid_format(request: PreparedRequest, *args, **kwargs) -> Response:
        return db_service_mock.generate_invalid_format(request)

    with mock.patch(SEND_METHOD, side_effect=generate_invalid_format) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

    assert response.status_code == 502

    data = response.get_json()

    assert 502 == data["code"]
    assert "InternalApiBadResponse" == data["error"]


def test_reports_when_invalid_argument_recieved(client) -> None:
    def generate_invalid_argument(
        request: PreparedRequest, *args, **kwargs
    ) -> Response:
        return db_service_mock.generate_invalid_argument(request)

    with mock.patch(SEND_METHOD, side_effect=generate_invalid_argument) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

    assert response.status_code == 502

    data = response.get_json()

    assert 502 == data["code"]
    assert "InternalApiBadResponse" == data["error"]


def test_reports_when_db_service_timeout(client) -> None:
    def generate_timeout(request: PreparedRequest, *args, **kwargs) -> Response:
        raise exceptions.Timeout()

    with mock.patch(SEND_METHOD, side_effect=generate_timeout) as _:
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

    assert response.status_code == 504

    data = response.get_json()

    assert 504 == data["code"]
    assert "InternalApiTimeout" == data["error"]
