import os
from pathlib import Path

import awsgi
import boto3

from rss_music_backend import create_app


# Some Python libraries depend on dynamic libraries Lambda doesn't package, so we store
# them in "lib" and point Python to them.
def assign_library_directory() -> None:
    path = Path(__file__).parent / "lib"
    previous_path = os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["LD_LIBRARY_PATH"] = f"{path}:{previous_path}"


# Populate secret "environment variables" from AWS SSM Parameters so they are read when
# app is created.
def populate_secrets() -> None:
    ssm_client = boto3.client("ssm")

    ssm_var_to_routes = {
        "PODCAST_INDEX_KEY_ROUTE": "RSS_PLAYER_PODCAST_INDEX_KEY",
        "PODCAST_INDEX_SECRET_ROUTE": "RSS_PLAYER_PODCAST_INDEX_SECRET",
    }

    for route_var, env_var in ssm_var_to_routes.items():
        route = os.environ[route_var]
        response = ssm_client.get_parameter(Name=route, WithDecryption=True)
        value = response["Parameter"]["Value"]
        os.environ[env_var] = value


# Move this to the database backend when we have it. This function (the internet
# backend function) will not have access to this.
# def get_rotated_secrets() -> None:
#    secrets_client = boto3.client("secretsmanager")
#
#    connection_url = os.environ["DATABASE_CONNECTION_PARTIAL"]
#
#    db_credentials = json.loads(
#        secrets_client.get_secret_value(
#            SecretId=os.environ["DATABASE_SECRET_ARN"]
#        )["SecretString"]
#    )
#
#    connection_url = connection_url.format(
#        user=db_credentials["username"],
#        password=db_credentials["password"]
#    )
#
#    return {
#        "DATABASE_CONNECTION": connection_url
#    }


assign_library_directory()
populate_secrets()
app = create_app()


# This is a short term solution! Most REST APIs for Lambda run on either AWS Lambda
# Powertools, and awsgi hasn't been maintained in years. However, to avoid a merge
# conflict and refactor, I'm using this for now.
def handler(event, context):
    # For the database backend when it exists.
    # secrets = get_rotated_secrets()
    # app.config.update(secrets)

    return awsgi.response(app, event, context)
