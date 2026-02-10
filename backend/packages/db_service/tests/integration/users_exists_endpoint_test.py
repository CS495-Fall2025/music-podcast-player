import pytest

from rss_music_data_model import User
from rss_music_db_service_schemas.users import (
    requests as db_requests,
    responses as db_responses,
)

ENDPOINT_URL = "/users/exists"


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


def test_existing_user_returns_true_by_id(client, db_session) -> None:
    user = User(
        username="testuser",
        email="testuser@domain.com",
        password=b"test-password-hash"
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        ENDPOINT_URL,
        json={
            "id": user.id,
        },
    )

    assert response.status_code == 200

    response_data = db_responses.UserExistsResponse().load(response.json())

    assert response_data["exists"] == True


def test_existing_user_returns_true_by_username(client, db_session) -> None:
    user = User(
        username="testuser",
        email="testuser@domain.com",
        password=b"test-password-hash"
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        ENDPOINT_URL,
        json={
            "username": user.username,
        },
    )

    assert response.status_code == 200

    response_data = db_responses.UserExistsResponse().load(response.json())

    assert response_data["exists"] == True


def test_existing_user_returns_true_by_email(client, db_session) -> None:
    user = User(
        username="testuser",
        email="testuser@domain.com",
        password=b"test-password-hash"
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        ENDPOINT_URL,
        json={
            "email": user.email,
        },
    )

    assert response.status_code == 200

    response_data = db_responses.UserExistsResponse().load(response.json())

    assert response_data["exists"] == True


def test_nonexistant_user_returns_false(client, db_session) -> None:
    user = User(
        username="testuser",
        email="testuser@domain.com",
        password=b"test-password-hash"
    )

    response = client.post(
        ENDPOINT_URL,
        json={
            "username": user.username,
        },
    )

    assert response.status_code == 200

    response_data = db_responses.UserExistsResponse().load(response.json())

    assert response_data["exists"] == False
