import os
from pathlib import Path

import pytest
from unittest import mock

from rss_music_api_service import create_app

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
    app.config.update({
        "TESTING": True,
    })

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
