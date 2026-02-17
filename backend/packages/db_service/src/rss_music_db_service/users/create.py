import hashlib
import os

from sqlalchemy.exc import IntegrityError

from rss_music_data_model import User, make_session
from rss_music_db_service.errors import NotUniqueError
from rss_music_db_service.logging_config import log_request, get_logger

logger = get_logger(__name__)


def create_and_add_user(username: str, email: str, password: str) -> None:
    user = _make_user(username, email, password)
    error = _attempt_add_user(user)

    if error:
        field = _parse_database_unique_constraint_error(error)
        raise NotUniqueError(field)


def _make_user(username: str, email: str, password: str) -> User:
    salt = os.urandom(16)
    # scrypt is recommended over bcrypt to prevent attacks from specialized
    # hardware
    hash = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=32
    )

    salt_and_hash_password = salt + hash
    return User(username=username, email=email, password=salt_and_hash_password)


# Returns None if successful, database error (str) if not.
def _attempt_add_user(user: User) -> None | str:
    with make_session() as session:
        try:
            session.add(user)
            session.commit()

            log_request(
                logger,
                "info",
                "db_change",
                "User created in database",
                operation="INSERT",
                table="users",
                username=user.username,
            )

            return None
        except IntegrityError as error:
            session.rollback()
            return str(error.orig)


# Yes this is arguably a weak solution, but the only way to determine which caused the
# error is to parse it out of the error message.
def _parse_database_unique_constraint_error(error: str) -> str:
    if "username" in error:
        return "username"

    if "email" in error:
        return "email"

    # Shouldn't occur, but just in case it does, this is a reasonable placeholder.
    return "unknown"
