import hashlib
import os
from datetime import datetime, timezone

from rss_music_data_model import User, make_session


def set_password_reset_code(email: str, code: str, expires_at: datetime) -> bool:
    with make_session() as session:
        user = session.query(User).filter(User.email == email).first()

        if user is None:
            return False

        user.password_reset_code = code
        user.password_reset_code_expires_at = expires_at
        session.commit()

        return True


def reset_password(email: str, code: str, new_password: str) -> bool:
    with make_session() as session:
        user = session.query(User).filter(User.email == email).first()

        if user is None:
            return False

        if user.password_reset_code != code:
            return False

        expires_at = user.password_reset_code_expires_at
        if expires_at is None or expires_at.replace(tzinfo=timezone.utc) < datetime.now(
            timezone.utc
        ):
            return False

        user.password = _salt_and_hash_password(new_password)
        user.password_reset_code = None
        user.password_reset_code_expires_at = None
        session.commit()

        return True


def _salt_and_hash_password(password: str) -> bytes:
    salt = os.urandom(16)
    password_hash = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=32
    )

    return salt + password_hash
