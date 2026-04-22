"""
Promotes an existing user to admin by email address.

Intended for production use. Requires DATABASE_URL to be set.

Usage:
    DATABASE_URL=<prod-url> python promote_to_admin.py
"""

import os
import sys

from rss_music_data_model import User, initialize_engine, make_session


def promote_to_admin(email: str) -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable is not set.", file=sys.stderr)
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
