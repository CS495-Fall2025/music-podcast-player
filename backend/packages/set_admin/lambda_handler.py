import json
import os
from pathlib import Path

import boto3
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError

import rss_music_data_model as data_model
from rss_music_set_admin import UserNotFoundError, set_admin


# Some Python libraries depend on dynamic libraries Lambda doesn't package, so we store
# them in "lib" and point Python to them.
def assign_library_directory() -> None:
    path = Path(__file__).parent / "lib"
    previous_path = os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["LD_LIBRARY_PATH"] = f"{path}:{previous_path}"


def get_db_connection_url() -> URL:
    if "DATABASE_INFO" not in os.environ:
        raise RuntimeError("Missing environment variable DATABASE_INFO")

    database_info = json.loads(os.environ["DATABASE_INFO"])

    rds_client = boto3.client("rds")
    token = rds_client.generate_db_auth_token(
        DBHostname=database_info["address"],
        Port=database_info["port"],
        DBUsername=database_info["role"],
        Region=database_info["region"],
    )

    connection_url = URL.create(
        drivername=database_info["driver"],
        username=database_info["role"],
        password=token,
        host=database_info["address"],
        port=database_info["port"],
        database=database_info["database"],
        query={"sslmode": "verify-full", "sslrootcert": "system"},
    )

    return connection_url


assign_library_directory()


def handler(event, _context):
    db_connection = get_db_connection_url()

    data_model.initialize_engine(db_connection)

    id_args = {}
    if "email" in event:
        id_args["email"] = event["email"]
    if "username" in event:
        id_args["username"] = event["username"]

    admin = event["admin"]
    with data_model.make_session() as session:
        try:
            set_admin(session, admin, **id_args)
        except ValueError as error:
            return {
                "error": "MissingArguments",
                "message": str(error),
            }
        except UserNotFoundError as error:
            return {
                "error": "UserNotFound",
                "message": str(error),
            }
        except OperationalError as error:
            return {
                "error": "OperationalError",
                "message": str(error),
            }

    return {"error": None}
