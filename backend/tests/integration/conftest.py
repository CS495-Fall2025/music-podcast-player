from pathlib import Path

import pytest
from unittest import mock

from rss_music_backend import create_app
from rss_music_backend.database import Base, get_engine, make_session

ALEMBIC_CONFIG_PATH = Path(__file__).parent.parent.parent / "alembic.ini"


@pytest.fixture
def app():
    app = create_app()

    # Allow exceptions to propegate and fail tests. Additionally, use an in-memory
    # SQLite database.
    app.config.update({"TESTING": True, "DATABASE_CONNECTION": "sqlite:///:memory:"})

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


@pytest.fixture
def db_session(app):
    with app.app_context():
        engine = get_engine()
        Base.metadata.create_all(engine)

        try:
            with make_session() as session:
                yield session
        finally:
            Base.metadata.drop_all(engine)
