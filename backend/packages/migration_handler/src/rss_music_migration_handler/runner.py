import logging
import os

from alembic import command
from alembic.config import Config

logging.basicConfig(level=logging.INFO)


def run() -> None:
    db_url = os.getenv("DATABASE_URL")

    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")
