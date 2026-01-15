from pathlib import Path

from alembic.config import Config
import alembic.command
import pytest
from unittest import mock

from rss_music_backend import create_app
from rss_music_backend.database import get_engine

ALEMBIC_CONFIG_PATH = Path(__file__).parent.parent.parent / "alembic.ini"


@pytest.fixture
def client():
    app = create_app()

    # Allow exceptions to propegate and fail tests. Additionally, use an in-memory
    # SQLite database.
    app.config.update(
        {
            "TESTING": True,
            "DATABASE_CONNECTION": "sqlite:///:memory:"
        }
    )

    # Bring the in-memory database to the latest migration.
    alembic_config = Config(ALEMBIC_CONFIG_PATH)
    alembic_config.set_main_option("sqlalchemy.url", "sqlite:///:memory:")

    with app.app_context():
        with get_engine().begin() as connection:
            alembic_config.attributes["connection"] = connection
            alembic.command.upgrade(alembic_config, "head")

    # Block network requests and fail the test. If network requests are intended, mock
    # them explicitly in the test.
    def fail_request(*args, **kwargs):
        assert False, (
            "Program attempted to make a network request when it shouldn't have"
        )

    with mock.patch("requests.Session.send", side_effect=fail_request) as _:
        yield app.test_client()
