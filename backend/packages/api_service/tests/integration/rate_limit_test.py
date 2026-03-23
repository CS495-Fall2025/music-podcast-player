import os
import time
import sys

import pytest
from requests import exceptions, PreparedRequest, Response

from tests.integration.api_mocks import podcastindex_mock
from tests.integration.helpers import ConstantResponse


@pytest.fixture
def valid_search(custom_responses) -> None:
    custom_responses[
        "https://api.podcastindex.org/api/1.0/search/music/byterm"
    ] = podcastindex_mock.generate_valid_response


def test_first_unauthenticated_request_creates_global_token_bucket(
    client, dynamodb
) -> None:
    token_bucket = dynamodb.Table("RequestLimits")

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    # Verify the bucket hasn't been created yet.
    assert "Item" not in db_response

    response = client.post("/auth/verify")
    assert response.status_code == 401

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response


def test_unauthenticated_request_creates_public_token_bucket(
    client, dynamodb
) -> None:
    token_bucket = dynamodb.Table("RequestLimits")

    db_response = token_bucket.get_item(Key={"user_id": "public"})
    # Verify the bucket hasn't been created yet.
    assert "Item" not in db_response

    response = client.post("/auth/verify")
    assert response.status_code == 401

    db_response = token_bucket.get_item(Key={"user_id": "public"})
    assert "Item" in db_response


def test_unauthenticated_request_uses_global_and_public_token(
    client, dynamodb
) -> None:
    token_bucket = dynamodb.Table("RequestLimits")

    token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })
    token_bucket.put_item(Item={
        "user_id": "public",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })

    response = client.post("/auth/verify")
    assert response.status_code == 401

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": "public"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]


def test_authenticated_request_uses_global_and_user_token(
    auth_client, user, dynamodb
) -> None:
    token_bucket = dynamodb.Table("RequestLimits")

    token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })
    token_bucket.put_item(Item={
        "user_id": "public",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })
    token_bucket.put_item(Item={
        "user_id": str(user.id),
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })

    response = auth_client.post("/auth/verify")
    assert response.status_code == 200

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": "public"})
    assert "Item" in db_response
    assert 5 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": str(user.id)})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]


def test_unauthenticated_search_uses_podcast_index_tokens(
    client, dynamodb, custom_responses
) -> None:
    custom_responses[
        "https://api.podcastindex.org/api/1.0/search/music/byterm"
    ] = podcastindex_mock.generate_valid_response

    token_bucket = dynamodb.Table("RequestLimits")

    db_response = token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })
    db_response = token_bucket.put_item(Item={
        "user_id": "public",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })

    response = client.get(
        "/search/feeds", query_string={"query": "query", "count": "5"}
    )
    assert response.status_code == 200 

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 4 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": "public"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 4 == db_response["Item"]["podcast_index"]


def test_authenticated_search_uses_podcast_index_tokens(
    auth_client, user, dynamodb, custom_responses
) -> None:
    custom_responses[
        "https://api.podcastindex.org/api/1.0/search/music/byterm"
    ] = podcastindex_mock.generate_valid_response

    token_bucket = dynamodb.Table("RequestLimits")

    db_response = token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })
    db_response = token_bucket.put_item(Item={
        "user_id": str(user.id),
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })

    response = auth_client.get(
        "/search/feeds", query_string={"query": "query", "count": "5"}
    )
    assert response.status_code == 200 

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 4 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": str(user.id)})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 4 == db_response["Item"]["podcast_index"]


def test_unauthenticated_request_fails_without_global_tokens(
    client, dynamodb
) -> None:
    token_bucket = dynamodb.Table("RequestLimits")

    token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 0,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })
    token_bucket.put_item(Item={
        "user_id": "public",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })

    response = client.post("/auth/verify")
    assert response.status_code == 429
    assert response.get_json()["error"] == "TooManyRequests"

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 0 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": "public"})
    assert "Item" in db_response
    assert 5 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]


def test_unauthenticated_request_fails_without_public_tokens(
    client, dynamodb
) -> None:
    token_bucket = dynamodb.Table("RequestLimits")

    token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })
    token_bucket.put_item(Item={
        "user_id": "public",
        "overall": 0,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })

    response = client.post("/auth/verify")
    assert response.status_code == 429
    assert response.get_json()["error"] == "TooManyRequests"

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 5 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": "public"})
    assert "Item" in db_response
    assert 0 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]


def test_unauthenticated_non_search_request_not_bound_by_podcastindex_tokens(
    client, dynamodb
) -> None:
    token_bucket = dynamodb.Table("RequestLimits")

    token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 0,
        "expiry": sys.maxsize,
    })
    token_bucket.put_item(Item={
        "user_id": "public",
        "overall": 5,
        "podcast_index": 0,
        "expiry": sys.maxsize,
    })

    response = client.post("/auth/verify")
    assert response.status_code == 401

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 0 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": "public"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 0 == db_response["Item"]["podcast_index"]


def test_unauthenticated_search_fails_without_podcast_index_tokens(
    client, dynamodb, custom_responses
) -> None:
    custom_responses[
        "https://api.podcastindex.org/api/1.0/search/music/byterm"
    ] = podcastindex_mock.generate_valid_response

    token_bucket = dynamodb.Table("RequestLimits")

    db_response = token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })
    db_response = token_bucket.put_item(Item={
        "user_id": "public",
        "overall": 5,
        "podcast_index": 0,
        "expiry": sys.maxsize,
    })

    response = client.get(
        "/search/feeds", query_string={"query": "query", "count": "5"}
    )
    assert response.status_code == 429
    assert response.get_json()["error"] == "TooManyRequests"

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 5 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": "public"})
    assert "Item" in db_response
    assert 5 == db_response["Item"]["overall"]
    assert 0 == db_response["Item"]["podcast_index"]


def test_authenticated_search_fails_without_podcast_index_tokens(
    auth_client, user, dynamodb, custom_responses
) -> None:
    custom_responses[
        "https://api.podcastindex.org/api/1.0/search/music/byterm"
    ] = podcastindex_mock.generate_valid_response

    token_bucket = dynamodb.Table("RequestLimits")

    db_response = token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })
    db_response = token_bucket.put_item(Item={
        "user_id": str(user.id),
        "overall": 5,
        "podcast_index": 0,
        "expiry": sys.maxsize,
    })

    response = auth_client.get(
        "/search/feeds", query_string={"query": "query", "count": "5"}
    )
    assert response.status_code == 429
    assert response.get_json()["error"] == "TooManyRequests"

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 5 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": str(user.id)})
    assert "Item" in db_response
    assert 5 == db_response["Item"]["overall"]
    assert 0 == db_response["Item"]["podcast_index"]


def test_refill_uses_expiration_of_current_time_plus_refill_seconds(
    app, client, dynamodb
) -> None:
    token_bucket = dynamodb.Table("RequestLimits")

    min_expiry = int(time.time()) + app.config["TOKEN_REFILL_SECONDS"]
    # Should create the bucket, thus refilling it automatically.
    response = client.post("/auth/verify")
    assert response.status_code == 401
    max_expiry = int(time.time()) + app.config["TOKEN_REFILL_SECONDS"]

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert "expiry" in db_response["Item"]

    # Since the refill occurs between when these two expiry times are calculated, it
    # should be between the two, no matter how long the request takes to complete.
    assert min_expiry <= db_response["Item"]["expiry"]
    assert max_expiry >= db_response["Item"]["expiry"]


def test_refill_occurs_on_or_after_expiration(
    app, client, dynamodb
) -> None:
    token_bucket = dynamodb.Table("RequestLimits")
   
    expiry = int(time.time())
    db_response = token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 5,
        "expiry": sys.maxsize,
    })
    db_response = token_bucket.put_item(Item={
        "user_id": "public",
        "overall": 0,
        "podcast_index": 0,
        "expiry": expiry,
    })

    response = client.post("/auth/verify")
    assert response.status_code == 401

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert 5 == db_response["Item"]["podcast_index"]
    
    db_response = token_bucket.get_item(Key={"user_id": "public"})
    assert "Item" in db_response
    assert (app.config["API_TOKENS_PER_REFILL"]["public"]["overall"] - 1
            == db_response["Item"]["overall"]
    )
    assert (app.config["API_TOKENS_PER_REFILL"]["public"]["podcast_index"]
            == db_response["Item"]["podcast_index"]
    )


def test_unauthenticated_search_penalized_on_podcast_index_too_many_requests(
    app, client, dynamodb, custom_responses
) -> None:
    custom_responses[
        "https://api.podcastindex.org/api/1.0/search/music/byterm"
    ] = ConstantResponse(429, {}) 

    token_bucket = dynamodb.Table("RequestLimits")

    db_response = token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 10,
        "expiry": sys.maxsize,
    })
    db_response = token_bucket.put_item(Item={
        "user_id": "public",
        "overall": 5,
        "podcast_index": 25,
        "expiry": sys.maxsize,
    })

    response = client.get(
        "/search/feeds", query_string={"query": "query", "count": "5"}
    )
    assert response.status_code == 503
    assert response.get_json()["error"] == "ExternalApiUnavaliable"

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert (max(9 - app.config["TOKEN_PENALTY"]["podcast_index"], 0)
            == db_response["Item"]["podcast_index"]
    )
    
    db_response = token_bucket.get_item(Key={"user_id": "public"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert (max(24 - app.config["TOKEN_PENALTY"]["podcast_index"], 0)
            == db_response["Item"]["podcast_index"]
    )


def test_authenticated_search_penalized_on_podcast_index_too_many_requests(
    app, auth_client, user, dynamodb, custom_responses
) -> None:
    custom_responses[
        "https://api.podcastindex.org/api/1.0/search/music/byterm"
    ] = ConstantResponse(429, {}) 

    token_bucket = dynamodb.Table("RequestLimits")

    db_response = token_bucket.put_item(Item={
        "user_id": "global",
        "overall": 5,
        "podcast_index": 20,
        "expiry": sys.maxsize,
    })
    db_response = token_bucket.put_item(Item={
        "user_id": str(user.id),
        "overall": 5,
        "podcast_index": 15,
        "expiry": sys.maxsize,
    })

    response = auth_client.get(
        "/search/feeds", query_string={"query": "query", "count": "5"}
    )
    assert response.status_code == 503
    assert response.get_json()["error"] == "ExternalApiUnavaliable"

    db_response = token_bucket.get_item(Key={"user_id": "global"})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert (max(19 - app.config["TOKEN_PENALTY"]["podcast_index"], 0)
            == db_response["Item"]["podcast_index"]
    )
    
    db_response = token_bucket.get_item(Key={"user_id": str(user.id)})
    assert "Item" in db_response
    assert 4 == db_response["Item"]["overall"]
    assert (max(14 - app.config["TOKEN_PENALTY"]["podcast_index"], 0)
            == db_response["Item"]["podcast_index"]
    )
