import boto3

from rss_music_dynamodb_tables.tables import TABLES


def ensure_dynamodb_tables(client=None) -> None:
    if client is None:
        client = boto3.resource("dynamodb")

    existing_tables = {table.name for table in client.tables.all()}

    for table_def in TABLES:
        if table_def["TableName"] in existing_tables:
            continue

        ttl = None
        if "_ttl" in table_def:
            ttl = table_def["_ttl"]
            del table_def["_ttl"]

        table = client.create_table(**table_def)
        table.wait_until_exists()

        if ttl is not None:
            client.update_time_to_live(
                TableName=table_def["TableName"],
                TimeToLiveSpecification=ttl,
            )
