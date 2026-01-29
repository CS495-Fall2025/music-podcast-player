from unittest import mock

import pytest
from requests import exceptions, PreparedRequest, Response

from tests.integration.api_mocks import podcastindex_mock
import urllib

ENDPOINT_URL = "/link/feed"
SEND_METHOD = "requests.Session.send"

def test_missing_url_returns_invalid_argument(client) -> None:
    response = client.get(ENDPOINT_URL)

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_count_too_low_returns_invalid_argument(client) -> None:
    response = client.get(ENDPOINT_URL, query_string={"query": "query", "count": "0"})

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_count_too_high_returns_invalid_argument(client) -> None:
    response = client.get(ENDPOINT_URL, query_string={"query": "query", "count": "51"})

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_empty_query_returns_invalid_argument(client) -> None:
    response = client.get(ENDPOINT_URL, query_string={"query": "", "count": "5"})

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_too_long_query_returns_invalid_argument(client) -> None:
    response = client.get(ENDPOINT_URL, query_string={"query": "a" * 256, "count": "5"})

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]

def test_invalid_url(client) -> None:
    response = client.get(ENDPOINT_URL, query_string={"query": urllib.parse.quote('https%3A%2F%2Fwww.google.com%2F')})

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]