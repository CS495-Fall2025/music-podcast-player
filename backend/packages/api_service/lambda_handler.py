import os
from pathlib import Path

import awsgi
import boto3

from rss_music_api_service import create_app


# Populate secret "environment variables" from AWS SSM Parameters so they are read when
# app is created.
def populate_static_secrets() -> None:
    ssm_client = boto3.client("ssm")

    ssm_var_to_routes = {
        "PODCAST_INDEX_KEY_ROUTE": "RSS_PLAYER_PODCAST_INDEX_KEY",
        "PODCAST_INDEX_SECRET_ROUTE": "RSS_PLAYER_PODCAST_INDEX_SECRET",
        # This should be rotated in the future! Currently, our app doesn't support this
        # (issues with refresh tokens would occur), so it's not currently rotated.
        "SECRET_KEY_ROUTE": "RSS_PLAYER_SECRET_KEY",
    }

    for route_var, env_var in ssm_var_to_routes.items():
        route = os.environ[route_var]
        response = ssm_client.get_parameter(Name=route, WithDecryption=True)
        value = response["Parameter"]["Value"]
        os.environ[env_var] = value


populate_static_secrets()
app = create_app()


# This is a short term solution! Most REST APIs for Lambda run on either AWS Lambda
# Powertools, and awsgi hasn't been maintained in years. However, to avoid a merge
# conflict and refactor, I'm using this for now.
def handler(event, context):
    return awsgi.response(app, event, context)
