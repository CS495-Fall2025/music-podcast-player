import boto3
import os

from rss_music_dynamodb_tables import ensure_dynamodb_tables


def main() -> None:
    ensure_dynamodb_tables(
        boto3.resource("dynamodb", endpoint_url=os.environ["DYNAMODB_URL"])
    )


if __name__ == "__main__":
    main()
