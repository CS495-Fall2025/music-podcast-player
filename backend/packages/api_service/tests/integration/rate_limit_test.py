import os

import pytest
from requests import exceptions, PreparedRequest, Response

from tests.integration.api_mocks import podcastindex_mock


@pytest.fixture
def valid_search(custom_responses) -> None:
    custom_responses[
        "https://api.podcastindex.org/api/1.0/search/music/byterm"
    ] = podcastindex_mock.generate_valid_response


def test_first_unauthenticated_request_creates_public_token_bucket(
    client, dynamodb
) -> None:
    token_bucket = dynamodb.Table("RequestLimits")

    # 0 is the public bucket because user IDs start at 1.
    db_response = token_bucket.get_item(Key={"user_id": "0"})
    # Verify the bucket hasn't been created yet.
    assert "Item" not in db_response

    response = client.post("/auth/verify")
    assert response.status_code == 401

    db_response = token_bucket.get_item(Key={"user_id": "0"})
    assert "Item" in db_response


#def test_simple_search(client, valid_search, dynamodb) -> None:
#    response = client.get(
#        "/search/feeds", query_string={"query": "query", "count": "5"}
#    )
#
#    assert response.status_code == 200
