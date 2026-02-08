from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


# These are effectively singletons.
_db_engine = None


def get_engine() -> Engine:
    if _db_engine is not None:
        return _db_engine

    raise RuntimeError("Database connection not initialized")


def make_session() -> Session:
    engine = get_engine()

    return Session(engine)


def initialize_engine(connection: str) -> None:
    global _db_engine

    # This is the setup for automated testing to avoid needing an actual DB. (Uses
    # SQLite in-memory DB.)
    if connection == "sqlite:///:memory:":
        _db_engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
    else:
        _db_engine = create_engine(connection)
