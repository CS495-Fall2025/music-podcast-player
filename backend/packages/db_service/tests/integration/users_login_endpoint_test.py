import hashlib
import os

from rss_music_data_model import User
from rss_music_db_service_schemas import ErrorResponse, ErrorType
from rss_music_db_service_schemas.users import (
    requests as db_requests,
    responses as db_responses,
)

ENDPOINT_URL = "/users/login"


def make_password_hash(password: str) -> bytes:
    salt = os.urandom(16)
    hash = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=32
    )
    
    return salt + hash


def test_empty_post_returns_invalid_format(client) -> None:
    response = client.post(ENDPOINT_URL)

    assert response.status_code == 400

    data = response.json()

    assert "InvalidFormat" == data["error"]


def test_malformed_post_returns_invalid_format(client) -> None:
    response = client.post(
        ENDPOINT_URL, content=b"NOT_JSON", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400

    data = response.json()

    assert "InvalidFormat" == data["error"]


def test_fail_to_login_to_nonexistant_user(client, db_session) -> None:
    response = client.post(
        ENDPOINT_URL,
        json={
            "username": "nonexistant",
            "password": "T3stP@ssw0rd",
        },
    )

    assert response.status_code == 401 

    response_data = ErrorResponse().load(response.json())

    assert ErrorType.INVALID_CREDENTIALS == response_data["error"]


def test_fail_to_login_wrong_password(client, db_session) -> None:
    username = "testuser"
    password = "T3stP@ssw0rd"

    user = User(
        username=username,
        email="testuser@domain.com",
        password=make_password_hash(password),
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        ENDPOINT_URL,
        json={
            "username": username,
            "password": "wr0ng_p@ssword",
        },
    )

    assert response.status_code == 401 

    response_data = ErrorResponse().load(response.json())

    assert ErrorType.INVALID_CREDENTIALS == response_data["error"]


def test_login_success(client, db_session) -> None:
    username = "testuser"
    password = "T3stP@ssw0rd"

    user = User(
        username=username,
        email="testuser@domain.com",
        password=make_password_hash(password),
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        ENDPOINT_URL,
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    response_data = db_responses.UserLoginResponse().load(response.json())

    assert user.id == response_data["id"]
    assert username == response_data["username"]

