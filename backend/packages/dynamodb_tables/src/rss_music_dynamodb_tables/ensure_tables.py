import boto3
import os

from rss_music_dynamodb_tables.tables import TABLES


def ensure_dynamodb_tables(client=None) -> None:
    if client is None:
        client = boto3.resource("dynamodb")

    existing_tables = {table.name for table in client.tables.all()}

    for table_def in TABLES:
        if table_def["TableName"].startswith("env:"):
            env_name = table_def["TableName"][4:]
            table_def["TableName"] = os.environ[env_name]
        if table_def["TableName"] in existing_tables:
            continue

        table = client.create_table(**table_def)
        table.wait_until_exists()
