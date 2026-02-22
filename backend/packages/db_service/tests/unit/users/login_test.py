import hashlib
import os

from rss_music_db_service.users import login


def test_login_correct_password() -> None:
    salt = os.urandom(16)
    password = "password"
    pass_bytes = password.encode("utf-8")
    password_hash = hashlib.scrypt(pass_bytes, salt=salt, n=16384, r=8, p=1, dklen=32)
    salted_hash = salt + password_hash

    assert login._verify_password(salted_hash, password) is True


def test_login_incorrect_password() -> None:
    salt = os.urandom(16)
    password = "password"
    pass_bytes = password.encode("utf-8")
    password_hash = hashlib.scrypt(pass_bytes, salt=salt, n=16384, r=8, p=1, dklen=32)
    salted_hash = salt + password_hash

    assert login._verify_password(salted_hash, "incorrect") is False
