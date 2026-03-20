from rss_music_dynamodb_tables import ensure_dynamodb_tables


def handler(event, context):
    if event.get("RequestType") == "Delete":
        return

    ensure_dynamodb_tables()
