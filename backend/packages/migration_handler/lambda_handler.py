import json
import os
from pathlib import Path

import rss_music_migration_handler


# Some Python libraries depend on dynamic libraries Lambda doesn't package, so we store
# them in "lib" and point Python to them.
def assign_library_directory() -> None:
    path = Path(__file__).parent / "lib"
    previous_path = os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["LD_LIBRARY_PATH"] = f"{path}:{previous_path}"


def get_secrets() -> None:
    connection_url = os.environ["DATABASE_URL_PARTIAL"]
    db_credentials = json.loads(os.environ["DATABASE_CREDENTIAL"])

    connection_url = connection_url.format(
        user=db_credentials["username"], password=db_credentials["password"]
    )

    return {"DATABASE_URL": connection_url}


def handler(event, context):
    if event.get("RequestType") == "Delete":
        return

    assign_library_directory()
    secrets = get_secrets()

    for env_name, value in secrets.items():
        os.environ[env_name] = value

    rss_music_migration_handler.run()
