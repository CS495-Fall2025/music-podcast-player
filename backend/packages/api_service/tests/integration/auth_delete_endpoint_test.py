import os

from helpers import ConstantResponse


def test_delete_without_auth_returns_unauthorized(client) -> None:
    """DELETE /auth/me without authentication returns 401."""
    response = client.delete("/auth/me")

    assert response.status_code == 401


def test_delete_with_valid_auth_deletes_user(auth_client, user, custom_responses) -> None:
    """DELETE /auth/me with valid auth deletes user and returns 200."""
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/{user.id}"] = (
        ConstantResponse(status_code=200, json_data={"success": True})
    )

    response = auth_client.delete("/auth/me")

    assert response.status_code == 200
    assert response.json["success"] is True


def test_delete_clears_session_cookies(auth_client, user, custom_responses) -> None:
    """DELETE /auth/me response clears authentication cookies."""
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/{user.id}"] = (
        ConstantResponse(status_code=200, json_data={"success": True})
    )

    response = auth_client.delete("/auth/me")

    assert response.status_code == 200
    cookie_headers = response.headers.getlist("Set-Cookie")
    assert any("access_token=" in header for header in cookie_headers)
    assert any("refresh_token=" in header for header in cookie_headers)


def test_delete_returns_not_found_when_user_missing(
    auth_client, user, custom_responses
) -> None:
    """DELETE /auth/me returns 404 if db-service reports user missing."""
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/{user.id}"] = (
        ConstantResponse(
            status_code=404,
            json_data={"error": "NotFound", "message": "User was not found"},
        )
    )

    response = auth_client.delete("/auth/me")

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"
