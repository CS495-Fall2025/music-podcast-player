import os

from fastapi import FastAPI

from rss_music_data_model import initialize_engine
from rss_music_db_service.routes import users
from rss_music_db_service.logging_config import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    
    initialize_engine(os.getenv("DATABASE_URL"))

    app = FastAPI()
    app.include_router(users, prefix="/users")

    return app
