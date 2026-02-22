import hashlib

from rss_music_data_model import User, make_session


def authenticate_user(username: str, password: str) -> User | None:
    with make_session() as session:
        user = session.query(User).filter(User.username == username).first()

        if not user:
            return

        if not _verify_password(user.password, password):
            return

        return user


def _verify_password(stored_salt_and_hash: bytes, provided_password: str) -> bool:
    """
    Verify a password against stored salt + hash.
    """
    salt = stored_salt_and_hash[:16]
    stored_hash = stored_salt_and_hash[16:]

    computed_hash = hashlib.scrypt(
        provided_password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=32
    )

    return computed_hash == stored_hash
