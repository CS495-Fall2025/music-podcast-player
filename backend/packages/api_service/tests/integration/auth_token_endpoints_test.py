import pytest
from sqlalchemy import select
import hashlib
import base64

from rss_music_backend.database import User
from rss_music_backend.auth.signup import create_and_add_user


def create_test_token(
    user_id, username, email, token_type="access", hours_until_expiry=1
):
    import jwt
    import os
    from datetime import datetime, timedelta, timezone

    secret_key = os.getenv("RSS_PLAYER_SECRET_KEY", "dev-secret-key")

    expiry_time = datetime.now(timezone.utc) + timedelta(hours=hours_until_expiry)

    token_data = {
        "sub": str(user_id),
        "name": username,
        "email": email,
        "type": token_type,
        "exp": expiry_time,
    }

    return jwt.encode(token_data, secret_key, algorithm="HS256")


@pytest.fixture
def test_user(db_session):
    username = "test_user"
    email = "test@example.com"
    password = "Password123!"

    create_and_add_user(username, email, password)

    query = select(User).where(User.username == username)
    user = db_session.execute(query).scalar_one()

    return {
        "username": username,
        "email": email,
        "password": password,
        "user_id": user.id,
    }


def generate_code_verifier():
    """Generate a PKCE code verifier."""
    return (
        base64.urlsafe_b64encode(b"test_verifier_string_12345678901234567890")
        .decode("utf-8")
        .rstrip("=")
    )


def generate_code_challenge(verifier):
    """Generate a PKCE code challenge from verifier."""
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


@pytest.fixture
def logged_in_client(client, test_user):
    """Create a logged-in client with valid tokens."""
    # Create tokens directly instead of going through login flow
    # This is more reliable for testing subsequent authenticated requests
    access_token = create_test_token(
        test_user["user_id"],
        test_user["username"],
        test_user["email"],
        token_type="access",
        hours_until_expiry=1,
    )
    refresh_token = create_test_token(
        test_user["user_id"],
        test_user["username"],
        test_user["email"],
        token_type="refresh",
        hours_until_expiry=168,
    )

    # Set cookies on the client
    client.set_cookie("access_token", access_token)
    client.set_cookie("refresh_token", refresh_token)

    return client


# ============================================================================
# /auth/verify endpoint tests
# ============================================================================


def test_verify_without_token_returns_error(client) -> None:
    """Test /auth/verify without any token."""
    response = client.post("/auth/verify")

    assert response.status_code == 401
    data = response.get_json()
    assert data["valid"] is False
    assert data["code"] == 401
    assert data["error"] == "MissingToken"


def test_verify_with_invalid_token_returns_error(client) -> None:
    """Test /auth/verify with malformed token."""
    client.set_cookie("access_token", "invalid.token.here")

    response = client.post("/auth/verify")

    assert response.status_code == 401
    data = response.get_json()
    assert data["valid"] is False
    assert data["code"] == 401
    assert data["error"] == "InvalidToken"


def test_verify_with_valid_token_returns_user_info(logged_in_client, test_user) -> None:
    """Test /auth/verify with valid access token."""
    response = logged_in_client.post("/auth/verify")

    assert response.status_code == 200
    data = response.get_json()

    assert data["valid"] is True
    assert "user" in data
    assert data["user"]["username"] == test_user["username"]
    assert data["user"]["email"] == test_user["email"]
    assert "id" in data["user"]


def test_verify_with_expired_token_returns_error(client, test_user) -> None:
    """Test /auth/verify with expired token."""
    expired_token = create_test_token(
        test_user["user_id"],
        test_user["username"],
        test_user["email"],
        token_type="access",
        hours_until_expiry=-1,  # Expired 1 hour ago
    )

    client.set_cookie("access_token", expired_token)

    response = client.post("/auth/verify")

    assert response.status_code == 401
    data = response.get_json()
    assert data["valid"] is False
    assert data["code"] == 401
    assert data["error"] == "InvalidToken"


def test_verify_with_wrong_token_type_returns_error(client, test_user) -> None:
    """Test /auth/verify with refresh token instead of access token."""
    refresh_token = create_test_token(
        test_user["user_id"],
        test_user["username"],
        test_user["email"],
        token_type="refresh",
        hours_until_expiry=168,  # 7 days
    )

    client.set_cookie("access_token", refresh_token)

    response = client.post("/auth/verify")

    assert response.status_code == 401
    data = response.get_json()
    assert data["valid"] is False


# ============================================================================
# /auth/refresh endpoint tests
# ============================================================================


def test_refresh_without_token_returns_error(client) -> None:
    """Test /auth/refresh without any refresh token."""
    response = client.post("/auth/refresh")

    assert response.status_code == 401
    data = response.get_json()
    assert data["code"] == 401
    assert data["error"] == "MissingToken"


def test_refresh_with_invalid_token_returns_error(client) -> None:
    """Test /auth/refresh with malformed token."""
    client.set_cookie("refresh_token", "invalid.token.here")

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    data = response.get_json()
    assert data["code"] == 401
    assert data["error"] == "InvalidToken"


def test_refresh_with_valid_token_returns_new_access_token(logged_in_client) -> None:
    """Test /auth/refresh with valid refresh token."""
    response = logged_in_client.post("/auth/refresh")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    # Check that a new access token was set
    access_token_found = False
    for header in response.headers.getlist("Set-Cookie"):
        if "access_token=" in header and "access_token=;" not in header:
            access_token_found = True
            break

    assert access_token_found


def test_refresh_with_expired_token_returns_error(client, test_user) -> None:
    """Test /auth/refresh with expired refresh token."""
    expired_token = create_test_token(
        test_user["user_id"],
        test_user["username"],
        test_user["email"],
        token_type="refresh",
        hours_until_expiry=-24,  # Expired 1 day ago
    )

    client.set_cookie("refresh_token", expired_token)

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    data = response.get_json()
    assert data["code"] == 401
    assert data["error"] == "InvalidToken"


def test_refresh_with_wrong_token_type_returns_error(client, test_user) -> None:
    """Test /auth/refresh with access token instead of refresh token."""
    access_token = create_test_token(
        test_user["user_id"],
        test_user["username"],
        test_user["email"],
        token_type="access",
        hours_until_expiry=1,
    )

    client.set_cookie("refresh_token", access_token)

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    data = response.get_json()
    assert data["code"] == 401
    assert data["error"] == "InvalidToken"


def test_refresh_with_deleted_user_returns_error(client, test_user, db_session) -> None:
    """Test /auth/refresh when the user has been deleted from database."""
    refresh_token = create_test_token(
        test_user["user_id"],
        test_user["username"],
        test_user["email"],
        token_type="refresh",
        hours_until_expiry=168,  # 7 days
    )

    client.set_cookie("refresh_token", refresh_token)

    # Delete the user from database
    query = select(User).where(User.id == test_user["user_id"])
    user = db_session.execute(query).scalar_one()
    db_session.delete(user)
    db_session.commit()

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    data = response.get_json()
    assert data["code"] == 401
    assert data["error"] == "UserNotFound"
    assert "not found" in data["message"].lower()


# ============================================================================
# /auth/logout endpoint tests
# ============================================================================


def test_logout_clears_cookies(logged_in_client) -> None:
    """Test /auth/logout clears authentication cookies."""
    response = logged_in_client.post("/auth/logout")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

    # Check that cookies were cleared (set to empty with max_age=0)
    cookies = {}
    for header in response.headers.getlist("Set-Cookie"):
        if "access_token=" in header:
            cookies["access_token"] = header
        elif "refresh_token=" in header:
            cookies["refresh_token"] = header

    # The cookies should exist but be empty
    assert "access_token" in cookies
    assert "refresh_token" in cookies
    assert "access_token=;" in cookies["access_token"]  # empty value
    assert "refresh_token=;" in cookies["refresh_token"]  # empty value
    assert "Max-Age=0" in cookies["access_token"]
    assert "Max-Age=0" in cookies["refresh_token"]


def test_logout_without_being_logged_in(client) -> None:
    """Test /auth/logout when not logged in (should still succeed)."""
    response = client.post("/auth/logout")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_logout_invalidates_access_token(logged_in_client) -> None:
    """Test that after logout, the old access token cannot be used."""
    # Verify we're logged in
    response = logged_in_client.post("/auth/verify")
    assert response.status_code == 200
    assert response.get_json()["valid"] is True

    # Logout
    response = logged_in_client.post("/auth/logout")
    assert response.status_code == 200

    # Try to verify again - should fail
    response = logged_in_client.post("/auth/verify")
    assert response.status_code == 401
    data = response.get_json()
    assert data["valid"] is False


def test_logout_invalidates_refresh_token(logged_in_client) -> None:
    """Test that after logout, the old refresh token cannot be used."""
    # Verify we can refresh
    response = logged_in_client.post("/auth/refresh")
    assert response.status_code == 200

    # Logout
    response = logged_in_client.post("/auth/logout")
    assert response.status_code == 200

    # Try to refresh again - should fail
    response = logged_in_client.post("/auth/refresh")
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


# ============================================================================
# /auth/ (PKCE initialization) endpoint tests
# ============================================================================


def test_auth_get_without_challenge_returns_error(client) -> None:
    """Test /auth/ without code_challenge parameter."""
    response = client.get("/auth/")

    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == 400
    assert data["error"] == "MissingParameter"
    assert "challenge" in data["message"].lower()


def test_auth_get_with_challenge_succeeds(client) -> None:
    """Test /auth/ with valid code_challenge."""
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)

    response = client.get(f"/auth/?code_challenge={challenge}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_auth_get_stores_challenge_in_session(client) -> None:
    """Test that /auth/ stores the challenge in session for later verification."""
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)

    # Store challenge
    response = client.get(f"/auth/?code_challenge={challenge}")
    assert response.status_code == 200
