import os
import apig_wsgi
import boto3
from requests_aws4auth import AWS4Auth

from rss_music_api_service import create_app
from rss_music_api_service.internal_apis import auth


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


def create_auth_generator() -> None:
    session = boto3.Session()
    credentials = session.get_credentials()
    auth_generator = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        "us-east-2",
        "execute-api",
        session_token=credentials.token,
    )

    auth.set_auth(auth_generator)


populate_static_secrets()
create_auth_generator()
app = create_app()
handler = apig_wsgi.make_lambda_handler(app)
