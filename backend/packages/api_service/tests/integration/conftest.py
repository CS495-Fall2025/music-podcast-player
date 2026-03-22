from collections import namedtuple
import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import boto3
import moto
import pytest
from unittest import mock

from rss_music_db_service_schemas.users.responses import UserLoginResponse
from rss_music_dynamodb_tables import ensure_dynamodb_tables

from rss_music_api_service import create_app
from rss_music_api_service.auth import pkce

import helpers
from helpers import ConstantResponse

ALEMBIC_CONFIG_PATH = Path(__file__).parent.parent.parent / "alembic.ini"


@pytest.fixture
def app():
    os.environ["RSS_PLAYER_ALLOWED_ORIGINS"] = "http://test.frontend.com"
    os.environ["RSS_PLAYER_PODCAST_INDEX_KEY"] = "test-index-api-key"
    os.environ["RSS_PLAYER_PODCAST_INDEX_SECRET"] = "test-index-api-secret"
    os.environ["RSS_PLAYER_SECRET_KEY"] = "test-secret-key-abcdefghijklmnopqrstuvwxyz"
    os.environ["RSS_PLAYER_DB_SERVICE_URL"] = "http://test.dbservice.com"

    app = create_app()

    # Allow unhandled exceptions to propegate and fail tests, but allow our defined 
    # error handlers to handle their respective exceptions.
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture
def client(app):
    # Block network requests and fail the test. If network requests are intended, mock
    # them explicitly in the test.
    def fail_request(request, **kwargs):
        url = urlunparse(urlparse(request.url)._replace(query="", fragment=""))
        assert False, (
            f"Unexpected network request made to {url}"
        )

    with mock.patch("requests.Session.send", side_effect=fail_request) as _:
        yield app.test_client()


# To use this fixture, put urls as keys and functions handling requests or
# ConstantResponses as values. MUST be placed after client in the test arguments. The
# key "_requests" can be used to get an array of all the requests made since the fixture
# started tracking.
@pytest.fixture
def custom_responses():
    responses = {"_requests": []}

    def handle_request(request, **kwargs):
        responses["_requests"].append(request)
        url = urlunparse(urlparse(request.url)._replace(query="", fragment=""))
        if url in responses:
            if callable(responses[url]):
                return responses[url](request)
            return responses[url].to_response()

        assert False, (
            f"Unexpected network request made to {url}"
        )

    with mock.patch("requests.Session.send", side_effect=handle_request) as _:
        yield responses


# This will NOT authenticate the client on it's own, only use this with the auth_client
# fixture for access to the user id and username.
@pytest.fixture
def user():
    User = namedtuple("User", ["username", "id"])

    return User("testuser123", 123)


# This fixture depends on authentication working correctly.
@pytest.fixture
def auth_client(client, user, custom_responses):
    custom_responses[
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/users/login"
    ] = ConstantResponse(
        status_code=200,
        json_data={
            "username": user.username,
            "id": user.id,
        }
    )
    custom_responses[
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/users/exists"
    ] = ConstantResponse(
        status_code=200,
        json_data={
            "exists": "true",
        }
    )

    verifier = "test_challenge"
    challenge = pkce.generate_code_challenge(verifier)

    # Send challenge
    response = client.get("/auth/", query_string={"code_challenge": challenge})
    assert response.status_code == 200, (
        "Error setting up authenticated user for test, PKCE challenge request failed: "
        f"{response.get_json()["message"]}"
    )

    # Login
    response = client.post(
        "/auth/login",
        json={
            "username": user.username,
            "password": "t3st_p@ssword",
            "code_verifier": verifier,
        },
    )
    assert response.status_code == 200, (
        "Error setting up authenticated user for test, login request failed: "
        f"{response.get_json()["message"]}"
    )

    del custom_responses[f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/users/login"]
    # exists handler left intentionally so the API service can authenticate the user
    # token.

    yield client


@pytest.fixture
def dynamodb():
    with moto.mock_aws():
        client = boto3.resource("dynamodb")
        ensure_dynamodb_tables(client)
        yield client
