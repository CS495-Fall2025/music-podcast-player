from unittest import mock

import pytest
from requests import PreparedRequest, Response, exceptions

from tests.integration.api_mocks import db_service_mock

ENDPOINT_URL = "/auth/signup"
VERIFY_ENDPOINT_URL = "/auth/signup/verify"
SEND_METHOD = "requests.Session.send"
SEND_VERIFICATION_METHOD = "rss_music_api_service.services.email_service.send_verification_code"
GENERATE_CODE_METHOD = "rss_music_api_service.routes.auth.email_codes.generate_code"


def test_empty_post_returns_invalid_format(client) -> None:
    response = client.post(ENDPOINT_URL)

    assert response.status_code == 400
    assert response.get_json()["error"] == "InvalidFormat"


def test_malformed_post_returns_invalid_format(client) -> None:
    response = client.post(
        ENDPOINT_URL, data="NOT_JSON", content_type="application/json"
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "InvalidFormat"


def test_missing_arg_returns_invalid_argument(client) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "t3st_user57",
            "email": "user@domain.com",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "InvalidArgument"


@pytest.mark.parametrize(
    "request_data",
    [
        {
            "username": "a" * 3,
            "email": "user@domain.com",
            "password": "Password123!",
        },
        {
            "username": "a" * 31,
            "email": "user@domain.com",
            "password": "Password123!",
        },
        {
            "username": "_admin",
            "email": "user@domain.com",
            "password": "Password123!",
        },
        {
            "username": "<user>",
            "email": "user@domain.com",
            "password": "Password123!",
        },
        {
            "username": "t3st_user57",
            "email": "domain.com",
            "password": "Password123!",
        },
        {
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": "@2abcdef",
        },
        {
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": "@2" + "a" * 80,
        },
        {
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": "123456789@%$#!",
        },
        {
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": "abcdefghijk@%$#!",
        },
        {
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": "a0b1c2d3e4f5g6h7",
        },
    ],
)
def test_invalid_signup_payload_returns_invalid_argument(client, request_data) -> None:
    response = client.post(ENDPOINT_URL, json=request_data)

    assert response.status_code == 400
    assert response.get_json()["error"] == "InvalidArgument"


def test_successful_signup_starts_verification(client) -> None:
    with mock.patch(SEND_VERIFICATION_METHOD):
        response = client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

    assert response.status_code == 201
    assert response.get_json()["verification_required"] is True


def test_signup_reports_email_delivery_failure(client) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 502
    assert response.get_json()["error"] == "EmailDeliveryFailed"


def test_signup_verify_rejects_without_pending_signup(client) -> None:
    response = client.post(
        VERIFY_ENDPOINT_URL,
        json={"code": "123456"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "InvalidSession"


def test_signup_verify_rejects_wrong_code(client) -> None:
    with mock.patch(SEND_VERIFICATION_METHOD), mock.patch(
        GENERATE_CODE_METHOD, return_value="123456"
    ):
        client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

    response = client.post(
        VERIFY_ENDPOINT_URL,
        json={"code": "654321"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "InvalidVerificationCode"


def test_signup_verify_creates_user_after_valid_code(client) -> None:
    def generate_success(request: PreparedRequest, *args, **kwargs) -> Response:
        assert request.url.endswith("/users/create")
        return db_service_mock.generate_users_create_success(request)

    with mock.patch(SEND_METHOD, side_effect=generate_success), mock.patch(
        SEND_VERIFICATION_METHOD
    ), mock.patch(GENERATE_CODE_METHOD, return_value="123456"):
        client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

        response = client.post(
            VERIFY_ENDPOINT_URL,
            json={"code": "123456"},
        )

    assert response.status_code == 201
    assert response.get_json()["verified"] is True
    assert response.get_json()["account_created"] is True


def test_signup_verify_duplicate_email_returns_error(client) -> None:
    def generate_duplicate_email(request: PreparedRequest, *args, **kwargs) -> Response:
        return db_service_mock.generate_users_create_not_unique(request, "email")

    with mock.patch(SEND_METHOD, side_effect=generate_duplicate_email), mock.patch(
        SEND_VERIFICATION_METHOD
    ), mock.patch(GENERATE_CODE_METHOD, return_value="123456"):
        client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

        response = client.post(
            VERIFY_ENDPOINT_URL,
            json={"code": "123456"},
        )

    assert response.status_code == 409
    assert response.get_json()["error"] == "ValueNotUnique"


def test_signup_verify_reports_db_timeout(client) -> None:
    def generate_timeout(request: PreparedRequest, *args, **kwargs) -> Response:
        raise exceptions.Timeout()

    with mock.patch(SEND_METHOD, side_effect=generate_timeout), mock.patch(
        SEND_VERIFICATION_METHOD
    ), mock.patch(GENERATE_CODE_METHOD, return_value="123456"):
        client.post(
            ENDPOINT_URL,
            json={
                "username": "t3st_user57",
                "email": "user@domain.com",
                "password": "Password123!",
            },
        )

        response = client.post(
            VERIFY_ENDPOINT_URL,
            json={"code": "123456"},
        )

    assert response.status_code == 504
    assert response.get_json()["error"] == "InternalApiTimeout"
