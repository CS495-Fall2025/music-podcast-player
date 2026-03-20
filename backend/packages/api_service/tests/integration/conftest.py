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

ALEMBIC_CONFIG_PATH = Path(__file__).parent.parent.parent / "alembic.ini"


@pytest.fixture
def app():
    os.environ["RSS_PLAYER_ALLOWED_ORIGINS"] = "http://test.frontend.com"
    os.environ["RSS_PLAYER_PODCAST_INDEX_KEY"] = "test-index-api-key"
    os.environ["RSS_PLAYER_PODCAST_INDEX_SECRET"] = "test-index-api-secret"
    os.environ["RSS_PLAYER_SECRET_KEY"] = "test-secret-key-abcdefghijklmnopqrstuvwxyz"
    os.environ["RSS_PLAYER_DB_SERVICE_URL"] = "http://test.dbservice.com"

    app = create_app()

    # Allow exceptions to propegate and fail tests.
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
    def fail_request(*args, **kwargs):
        assert False, (
            "Program attempted to make a network request when it shouldn't have"
        )

    with mock.patch("requests.Session.send", side_effect=fail_request) as _:
        yield app.test_client()


# To use this fixture, put urls as keys and functions handling requests as values. MUST
# be placed after client in the test arguments.
@pytest.fixture
def custom_responses():
    responses = {}

    def handle_request(request, **kwargs):
        url = urlunparse(urlparse(request.url)._replace(query="", fragment=""))
        if url in responses:
            return responses[url](request)

        assert False, (
            f"Unexpected network request made to {url}"
        )

    with mock.patch("requests.Session.send", side_effect=handle_request) as _:
        yield responses


# This will NOT authenticate the client on it's own, only use this with the auth_client
# fixture for access to the user id and username.
def user():
    User = namedtuple("User", ["username", "id"])

    return User("testuser123", 123)


# This fixture depends on authentication working correctly.
@pytest.fixture
def auth_client(client, user):
    def db_authenticated(request, **kwargs):
        url = urlunparse(urlparse(request.url)._replace(query="", fragment=""))
        if url == f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/auth/login":
            data = {
                "username": user.username,
                "id": user.id,
            }
            data = UserLoginResponse().dump(data)
            
            return helpers.make_response(data, 200)

        assert False, (
            "Error setting up authenticated user for test, unexpected request to "
            f"{url}"
        )

    with mock.patch("requests.Session.send", side_effect=db_authenticated) as _:
        verifier = "test_challenge"
        challenge = pkce.generate_code_challenge(challenge)

        # Send challenge
        response = client.get("/auth/", params={"code_challenge": challenge})
        assert response.status_code == 200, (
            "Error setting up authenticated user for test, PKCE challenge request failed"
        )

        # Login
        response = client.post(
            "/auth/login",
            json={
                "username": user.username,
                "password": "test_password",
                "code_verifier": verifier,
            },
        )
        assert response.status_code == 200, (
            "Error setting up authenticated user for test, login request failed"
        )


@pytest.fixture
def dynamodb():
    with moto.mock_aws():
        client = boto3.resource("dynamodb")
        ensure_dynamodb_tables(client)
        yield client
