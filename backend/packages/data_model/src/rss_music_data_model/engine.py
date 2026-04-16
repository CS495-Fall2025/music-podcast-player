from sqlalchemy import create_engine, Engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


# These are effectively singletons.
_db_engine = None


def _enable_sqlite_foreign_keys(engine: Engine) -> Engine:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def get_engine() -> Engine:
    if _db_engine is not None:
        return _db_engine

    raise RuntimeError("Database connection not initialized")


def make_session() -> Session:
    engine = get_engine()

    return Session(engine)


def initialize_engine(connection: str | URL) -> None:
    global _db_engine

    # This is the setup for automated testing to avoid needing an actual DB. (Uses
    # SQLite in-memory DB.)
    if connection == "sqlite:///:memory:":
        _db_engine = _enable_sqlite_foreign_keys(
            create_engine(
                "sqlite:///:memory:",
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
            )
        )
    else:
        _db_engine = create_engine(connection)
