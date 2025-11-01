import pytest
from unittest import mock

from rss_music_backend import create_app


@pytest.fixture
def client():
    app = create_app()

    # Allow exceptions to propegate
    app.config.update(
        {
            "TESTING": True,
        }
    )

    def fail_request(*args, **kwargs):
        assert False, (
            "Program attempted to make a network request when it shouldn't have"
        )

    with mock.patch("requests.Session.send", side_effect=fail_request) as _:
        yield app.test_client()

    # Reset any persisted resources here.
