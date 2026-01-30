import os

import boto3

from rss_music_backend import create_app


# Populate secret "environment variables" from AWS SSM Parameters so they are read when
# app is created.

def populate_secrets() -> None:
    ssm_client = boto3.client("ssm")

    var_to_routes = {
        "SSM_ROUTE_PODCAST_INDEX_KEY": "RSS_PLAYER_PODCAST_INDEX_KEY",
        "SSM_ROUTE_PODCAST_INDEX_SECRET": "RSS_PLAYER_PODCAST_INDEX_SECRET",
        "SSM_ROUTE_DATABASE_CONNECTION": "RSS_PLAYER_DATABASE_CONNECTION",
    }

    for route_var, env_var in var_to_routes.items():
        route = os.environ[route_var]
        value = ssm_client.get_parameter(Name=route, WithDecryption=True)
        os.environ[env_var] = value


populate_secrets()
app = create_app()


# This is a short term solution! Most REST APIs for Lambda run on either AWS Lambda
# Powertools, and awsgi hasn't been maintained in years. However, to avoid a merge 
# conflict and refactor, I'm using this for now.
def handler(event, context):
    return awsgi.response(app, event, context)
