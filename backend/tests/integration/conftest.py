import pytest

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

    yield app.test_client()

    # Reset any persisted resources here.
