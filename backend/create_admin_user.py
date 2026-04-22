"""
Creates an admin user directly in the database for local development/testing.

Usage:
    cd backend\packages\db_service
    uv run python ..\..\create_admin_user.py

Defaults to connecting to the local dev database (postgresql://postgres:dev-db-password@localhost/postgres).
Override with the DATABASE_URL environment variable.
"""

import argparse
import hashlib
import os
import sys

from rss_music_data_model import User, initialize_engine, make_session


DEFAULT_DATABASE_URL = "postgresql://postgres:dev-db-password@localhost/postgres"
DEFAULT_USERNAME = "adminAccount"
DEFAULT_EMAIL = "admin@localhost"
DEFAULT_PASSWORD = "Password123!"


def hash_password(password: str) -> bytes:
    salt = os.urandom(16)
    hashed = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=32
    )
    return salt + hashed


def create_admin(username: str, email: str, password: str) -> None:
    db_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    initialize_engine(db_url)

    with make_session() as session:
        existing = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing:
            existing.username = username
            existing.email = email
            existing.password = hash_password(password)
            existing.is_admin = True
            existing.email_verified = True
            session.commit()
            print(f"Admin user updated: username='{existing.username}' email='{existing.email}'")
            return

        user = User(
            username=username,
            email=email,
            password=hash_password(password),
            email_verified=True,
            profile_public=False,
            is_admin=True,
        )
        session.add(user)
        session.commit()
        print(f"Admin user created: username='{username}' email='{email}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an admin user for local testing.")
    parser.add_argument("--username", default=DEFAULT_USERNAME)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    args = parser.parse_args()

    try:
        create_admin(args.username, args.email, args.password)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
