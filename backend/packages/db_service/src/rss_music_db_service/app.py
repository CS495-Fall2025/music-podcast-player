import os

from fastapi import FastAPI
from sqlalchemy.engine import URL

from rss_music_data_model import initialize_engine
from rss_music_db_service.routes import users
from rss_music_db_service.routes import playlists
from rss_music_db_service.logging_config import configure_logging


def create_app(url_override: str | URL = None) -> FastAPI:
    configure_logging()

    db_connection = (
        url_override if url_override is not None else os.environ["DATABASE_URL"]
    )
    initialize_engine(db_connection)

    app = FastAPI()
    app.include_router(users, prefix="/users")
    app.include_router(playlists, prefix="/playlists")

    return app
