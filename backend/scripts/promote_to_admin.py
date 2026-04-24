"""
Promotes an existing user to admin by email address.

Intended for production use. Requires DATABASE_URL to be set.

Usage:
    DATABASE_URL=<prod-url> python promote_to_admin.py
    # or
    RSS_PLAYER_DATABASE_CONNECTION=<prod-url> python promote_to_admin.py
"""

import os
import sys
from pathlib import Path
from sqlalchemy.engine import make_url

try:
    from rss_music_data_model import User, initialize_engine, make_session
except ModuleNotFoundError as exc:
    if exc.name != "rss_music_data_model":
        raise

    local_data_model_src = (
        Path(__file__).resolve().parent / "packages" / "data_model" / "src"
    )
    sys.path.insert(0, str(local_data_model_src))
    from rss_music_data_model import User, initialize_engine, make_session


def _read_backend_env_database_url() -> str | None:
    env_path = Path(__file__).resolve().parent.parent / "secrets" / "backend.env"
    if not env_path.exists():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        if key.strip() == "RSS_PLAYER_DATABASE_CONNECTION":
            return value.strip().strip('"').strip("'")

    return None


def _get_database_url() -> str | None:
    db_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("RSS_PLAYER_DATABASE_CONNECTION")
        or _read_backend_env_database_url()
    )

    if not db_url:
        return None

    return _normalize_database_host_for_local_run(db_url)


def _normalize_database_host_for_local_run(db_url: str) -> str:
    # In secrets/backend.env, the database host is "database" for Docker network use.
    # When this script runs on the host machine, that hostname does not resolve.
    is_in_container = Path("/.dockerenv").exists()
    if is_in_container:
        return db_url

    try:
        parsed = make_url(db_url)
    except Exception:
        return db_url

    if parsed.host != "database":
        return db_url

    updated = parsed.set(host="localhost")
    return updated.render_as_string(hide_password=False)


def promote_to_admin(email: str) -> None:
    db_url = _get_database_url()
    if not db_url:
        print(
            "Error: Set DATABASE_URL (or RSS_PLAYER_DATABASE_CONNECTION) before running this script.",
            file=sys.stderr,
        )
        sys.exit(1)

    initialize_engine(db_url)

    with make_session() as session:
        user = session.query(User).filter(User.email == email).first()

        if not user:
            print(f"Error: No user found with email '{email}'.", file=sys.stderr)
            sys.exit(1)

        if user.is_admin:
            print(f"User '{user.username}' ({email}) is already an admin.")
            return

        user.is_admin = True
        session.commit()
        print(f"Success: '{user.username}' ({email}) has been promoted to admin.")


if __name__ == "__main__":
    print("=== Promote user to admin ===")
    email = input("Enter the email address of the user to promote: ").strip()

    if not email:
        print("Error: Email cannot be empty.", file=sys.stderr)
        sys.exit(1)

    confirm = input(f"Promote '{email}' to admin? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        sys.exit(0)

    try:
        promote_to_admin(email)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
