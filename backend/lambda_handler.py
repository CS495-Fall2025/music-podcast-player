import json
import os

import awsgi
import boto3

from rss_music_backend import create_app


# Populate secret "environment variables" from AWS SSM Parameters so they are read when
# app is created.

def populate_secrets() -> None:
    ssm_client = boto3.client("ssm")
    secrets_client = boto3.client("secretsmanager")

    ssm_var_to_routes = {
        "SSM_ROUTE_PODCAST_INDEX_KEY": "RSS_PLAYER_PODCAST_INDEX_KEY",
        "SSM_ROUTE_PODCAST_INDEX_SECRET": "RSS_PLAYER_PODCAST_INDEX_SECRET",
    }

    for route_var, env_var in ssm_var_to_routes.items():
        route = os.environ[route_var]
        response = ssm_client.get_parameter(Name=route, WithDecryption=True)
        value = response["Parameter"]["Value"]
        os.environ[env_var] = value

    # Populate database connection string.
    connection_url = os.environ["DATABASE_CONNECTION_PARTIAL"]

    db_credentials = json.loads(
        secrets_client.get_secret_value(
            SecretId=os.environ["DATABASE_SECRET_ARN"]
        )["SecretString"]
    )

    connection_url = connection_url.format(
        user=db_credentials["username"],
        password=db_credentials["password"]
    )

    os.environ["RSS_PLAYER_DATABASE_CONNECTION"] = connection_url


populate_secrets()
app = create_app()


# This is a short term solution! Most REST APIs for Lambda run on either AWS Lambda
# Powertools, and awsgi hasn't been maintained in years. However, to avoid a merge 
# conflict and refactor, I'm using this for now.
def handler(event, context):
    return awsgi.response(app, event, context)
