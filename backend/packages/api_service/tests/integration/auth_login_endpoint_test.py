import pytest
from sqlalchemy import select
import hashlib
import base64

from rss_music_backend.database import User
from rss_music_backend.auth.signup import create_and_add_user

ENDPOINT_URL = "/auth/login"


@pytest.fixture
def test_user(db_session):
    """Create a test user for login tests."""
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


def test_invalid_username_returns_error(client, test_user, pkce_challenge) -> None:
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


def test_invalid_password_returns_error(client, test_user, pkce_challenge) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": test_user["username"],
            "password": "WrongPassword123!",
            "code_verifier": pkce_challenge["verifier"],
        },
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data["code"] == 401
    assert data["error"] == "InvalidCredentials"
    assert "credentials" in data["message"].lower()


def test_successful_login_returns_cookies(client, test_user, pkce_challenge) -> None:
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


def test_successful_login_clears_pkce_from_session(
    client, test_user, pkce_challenge
) -> None:
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
