import pytest
from sqlalchemy import select

from rss_music_backend.database import User

ENDPOINT_URL = "/auth/signup"


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


def test_successful_signup(client, db_session) -> None:
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

    query = select(User).where(User.username == "t3st_user57")
    results = list(db_session.execute(query).scalars())

    assert 1 == len(results)


def test_duplicate_username_returns_error(client, db_session) -> None:
    client.post(
        ENDPOINT_URL,
        json={
            "username": "t3st_user57",
            "email": "otheruser@domain.com",
            "password": "OtherPassword123!",
        },
    )
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": "Password123!",
        },
    )

    query = select(User).where(User.username == "t3st_user57")
    results = list(db_session.execute(query).scalars())
    print([result.__dict__ for result in results])

    assert response.status_code == 403

    data = response.get_json()

    assert 403 == data["code"]
    assert "username" == data["field"]
    assert "This username is already in use" == data["message"]


def test_duplicate_email_returns_error(client, db_session) -> None:
    client.post(
        ENDPOINT_URL,
        json={
            "username": "0ther_t3st_user57",
            "email": "user@domain.com",
            "password": "OtherPassword123!",
        },
    )
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "t3st_user57",
            "email": "user@domain.com",
            "password": "Password123!",
        },
    )

    query = select(User).where(User.username == "t3st_user57")
    results = list(db_session.execute(query).scalars())
    print([result.__dict__ for result in results])

    assert response.status_code == 403

    data = response.get_json()

    assert 403 == data["code"]
    assert "email" == data["field"]
    assert "This email is already in use" == data["message"]
