from argparse import ArgumentParser, Namespace
import os
import sys

from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

import rss_music_data_model as data_model
from rss_music_set_admin import UserNotFoundError, set_admin


load_dotenv()


def parse_args() -> Namespace:
    parser = ArgumentParser(
        prog="setadmin",
        description="Mark or unmark a user as admin",
    )

    parser.add_argument("identifier", help="The username or email of the user")
    parser.add_argument(
        "-d",
        "--demote",
        action="store_true",
        help="Remove the user's admin status instead of making them an admin",
    )
    parser.add_argument(
        "-e",
        "--email",
        action="store_true",
        help="Indicates that the identifier is an email",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        db_url = os.environ["DATABASE_URL"]
    except KeyError:
        print(
            "A database connection url must be provided as DATABASE_URL",
            file=sys.stderr,
        )
        sys.exit(1)

    data_model.initialize_engine(db_url)

    identifier_type = "email" if args.email else "username"
    identifier_arg = {identifier_type: args.identifier}
    with data_model.make_session() as session:
        try:
            set_admin(session, not args.demote, **identifier_arg)
            if args.demote:
                print("Successfully removed user as an admin")
            else:
                print("Successfully made user an admin")
        except UserNotFoundError:
            print(f"Could not find a user with that {identifier_type}", file=sys.stderr)
            sys.exit(1)
        except OperationalError as error:
            print(f"Failed to set admin status of user:\n{error}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
