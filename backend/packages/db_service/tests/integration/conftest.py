import os
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from rss_music_data_model import Base, get_engine, make_session

from rss_music_db_service.app import create_app


@pytest.fixture
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    app = create_app()

    yield app


@pytest.fixture
def client(app):
    yield TestClient(app)


@pytest.fixture
def db_session(app):
    engine = get_engine()
    Base.metadata.create_all(engine)

    try:
        with make_session() as session:
            yield session
    finally:
        Base.metadata.drop_all(engine)
