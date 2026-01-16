import hashlib

import pytest

from rss_music_backend.auth import signup
from rss_music_backend.database.users import User


def test_makes_user_with_username() -> None:
    expected = "username"
    user = signup._make_user(expected, "email@domain.com", "password")

    assert expected == user.username


def test_makes_user_with_email() -> None:
    expected = "email@domain.com"
    user = signup._make_user("username", expected, "password")

    assert expected == user.email


def test_makes_user_with_hashed_and_salted_password() -> None:
    password = "password"
    user = signup._make_user("username", "email@domain.com", password)

    pass_bytes = password.encode("utf-8")
    salt = user.password[:16]
    actual_hash = user.password[16:]

    expected_hash = hashlib.scrypt(pass_bytes, salt=salt, n=16384, r=8, p=1, dklen=32)

    assert expected_hash == actual_hash


@pytest.mark.parametrize(
    "error",
    [
        # Postgres
        'duplicate key value violates unique constraint "users_username_key"',
        # MySQL
        "Duplicate entry 'foo@example.com' for key 'users.username'",
        # SQLite
        "UNIQUE constraint failed: users.username",
    ],
)
def test_identifies_username_not_unique_error(error) -> None:
    actual = signup._parse_database_unique_constraint_error(error)

    assert "username" == actual


@pytest.mark.parametrize(
    "error",
    [
        # Postgres
        'duplicate key value violates unique constraint "users_email_key"',
        # MySQL
        "Duplicate entry 'foo@example.com' for key 'users.email'",
        # SQLite
        "UNIQUE constraint failed: users.email",
    ],
)
def test_identifies_email_not_unique_error(error) -> None:
    actual = signup._parse_database_unique_constraint_error(error)

    assert "email" == actual
