import json
import os
from pathlib import Path

import boto3
from mangum import Mangum

from rss_music_db_service.app import create_app


# Some Python libraries depend on dynamic libraries Lambda doesn't package, so we store
# them in "lib" and point Python to them.
def assign_library_directory() -> None:
    path = Path(__file__).parent / "lib"
    previous_path = os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["LD_LIBRARY_PATH"] = f"{path}:{previous_path}"


def get_rotated_secrets() -> None:
    secrets_client = boto3.client("secretsmanager")

    connection_url = os.environ["DATABASE_URL_PARTIAL"]

    db_credentials = json.loads(
        secrets_client.get_secret_value(
            SecretId=os.environ["DATABASE_SECRET_ARN"]
        )["SecretString"]
    )

    connection_url = connection_url.format(
        user=db_credentials["username"],
        password=db_credentials["password"]
    )

    return {
        "DATABASE_URL": connection_url
    }


assign_library_directory()
app_handler = None


def handler(event, context):
    global app_handler
    secrets = get_rotated_secrets()

    secrets_updated = False
    for env_name, value in secrets.items():
        if env_name in os.environ and os.environ[env_name] == value:
            continue
        os.environ[env_name] = value
        secrets_updated = True

    if secrets_updated:
        app_handler = Mangum(create_app())

    return app_handler(event, context)
