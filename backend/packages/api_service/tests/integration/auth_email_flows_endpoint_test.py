from unittest import mock

from requests import PreparedRequest, Response

from tests.integration.api_mocks import db_service_mock

SEND_METHOD = "requests.Session.send"
SEND_VERIFICATION_METHOD = "rss_music_api_service.services.email_service.send_verification_code"
SEND_RESET_METHOD = "rss_music_api_service.services.email_service.send_password_reset_code"


def test_verify_email_success(client) -> None:
    def generate_success(request: PreparedRequest, *args, **kwargs) -> Response:
        assert request.url.endswith("/users/verify-email")
        return db_service_mock.generate_operation_success(True)

    with mock.patch(SEND_METHOD, side_effect=generate_success) as _:
        response = client.post(
            "/auth/verify-email",
            json={"email": "user@domain.com", "code": "123456"},
        )

    assert response.status_code == 200
    assert response.get_json()["verified"] is True


def test_verify_email_invalid_code(client) -> None:
    def generate_failure(request: PreparedRequest, *args, **kwargs) -> Response:
        assert request.url.endswith("/users/verify-email")
        return db_service_mock.generate_operation_success(False)

    with mock.patch(SEND_METHOD, side_effect=generate_failure) as _:
        response = client.post(
            "/auth/verify-email",
            json={"email": "user@domain.com", "code": "123456"},
        )

    assert response.status_code == 400
    assert response.get_json()["error"] == "InvalidVerificationCode"


def test_forgot_password_sends_email_when_user_exists(client) -> None:
    def generate_success(request: PreparedRequest, *args, **kwargs) -> Response:
        assert request.url.endswith("/users/set-password-reset-code")
        return db_service_mock.generate_operation_success(True)

    with mock.patch(SEND_METHOD, side_effect=generate_success) as _, mock.patch(
        SEND_RESET_METHOD
    ) as send_reset:
        response = client.post(
            "/auth/forgot-password",
            json={"email": "user@domain.com"},
        )

    assert response.status_code == 200
    assert response.get_json()["success"] is True
    send_reset.assert_called_once()


def test_reset_password_invalid_code(client) -> None:
    def generate_failure(request: PreparedRequest, *args, **kwargs) -> Response:
        assert request.url.endswith("/users/reset-password")
        return db_service_mock.generate_operation_success(False)

    with mock.patch(SEND_METHOD, side_effect=generate_failure) as _:
        response = client.post(
            "/auth/reset-password",
            json={
                "email": "user@domain.com",
                "code": "123456",
                "new_password": "Password123!",
            },
        )

    assert response.status_code == 400
    assert response.get_json()["error"] == "InvalidResetCode"
