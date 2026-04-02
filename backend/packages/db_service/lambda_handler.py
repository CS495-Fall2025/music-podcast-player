import json
import os
from pathlib import Path

import boto3
from mangum import Mangum
from sqlalchemy.engine import URL

from rss_music_db_service.app import create_app


# Some Python libraries depend on dynamic libraries Lambda doesn't package, so we store
# them in "lib" and point Python to them.
def assign_library_directory() -> None:
    path = Path(__file__).parent / "lib"
    previous_path = os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["LD_LIBRARY_PATH"] = f"{path}:{previous_path}"


def get_db_connection_url() -> URL:
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
#app_handler = None


def handler(event, context):
    # Intentionally not caching this for now, DB tokens only last 15 minutes.
    #global app_handler

    #if secrets_updated:
    db_connection = get_db_connection_url()
    app_handler = Mangum(create_app(db_connection))

    return app_handler(event, context)
