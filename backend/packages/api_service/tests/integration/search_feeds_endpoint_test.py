from unittest import mock

import pytest
from requests import exceptions, PreparedRequest, Response

from tests.integration.api_mocks import podcastindex_mock

ENDPOINT_URL = "/search/feeds"
SEND_METHOD = "requests.Session.send"


def test_missing_query_returns_invalid_argument(client) -> None:
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


# Includes a varity of SQL Injection / XXS Attempt inputs
@pytest.mark.parametrize(
    "query",
    [
        "' OR '1'='1",
        '" OR "1"="1',
        "admin' --",
        "admin' #",
        "admin'/*",
        "0 OR 1=1",
        "1; DROP TABLE users; --",
        "'; DROP TABLE users; --",
        "' UNION SELECT NULL --",
        '" UNION SELECT 1,2,3 --',
        "Robert'); DROP TABLE Students;--",
        "' OR 'a'='a",
        "0x414243 OR 1=1",
        "%' OR '%'='%",
        "' OR (SELECT count(*) FROM users) > 0 --",
        "' OR '' = '",
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<a href='javascript:alert(1)'>x</a>",
        '" onmouseover=alert(1) "',
        "' onfocus=alert(1) '",
        "&lt;script&gt;alert(1)&lt;/script&gt;",
        "<svg/onload=alert(1)>",
        "<scr<script>ipt>alert(1)</script>",
        '<iframe srcdoc="<script>alert(1)</script>"></iframe>',
        '<div style="background-image: url(javascript:alert(1))">x</div>',
        "${alert(1)}",
        "javascript:alert(String.fromCharCode(88,83,83))",
    ],
)
def test_illegal_characters_in_query_returns_invalid_argument(client, query) -> None:
    response = client.get(ENDPOINT_URL, query_string={"query": query, "count": "5"})

    assert response.status_code == 400

    data = response.get_json()

    assert 400 == data["code"]

    assert "InvalidArgument" == data["error"]


def test_valid_query_returns_valid_data(client) -> None:
    def get_valid_response(request: PreparedRequest, *args, **kwargs) -> Response:
        return podcastindex_mock.generate_valid_response(request)

    with mock.patch(SEND_METHOD, side_effect=get_valid_response) as _:
        response = client.get(
            ENDPOINT_URL, query_string={"query": "query", "count": "5"}
        )

        assert response.status_code == 200

        data = response.get_json()

        assert 200 == data["code"]

        assert "https://rss.net/feed0" == data["feeds"][0]["url"]
        assert "https://image.net/artwork/feed0" == data["feeds"][0]["art_url"]
        assert "title0" == data["feeds"][0]["title"]
        assert "artist0" == data["feeds"][0]["artist"]


def test_limits_to_count(client) -> None:
    def get_valid_response(request: PreparedRequest, *args, **kwargs) -> Response:
        return podcastindex_mock.generate_valid_response(request)

    with mock.patch(SEND_METHOD, side_effect=get_valid_response) as _:
        response = client.get(
            ENDPOINT_URL, query_string={"query": "query", "count": "10"}
        )

        assert response.status_code == 200

        data = response.get_json()

        assert 200 == data["code"]

        assert "title0" == data["feeds"][0]["title"]
        assert "title9" == data["feeds"][9]["title"]
        assert 10 == len(data["feeds"])


def test_paging_correct(client) -> None:
    def get_valid_response(request: PreparedRequest, *args, **kwargs) -> Response:
        return podcastindex_mock.generate_valid_response(request)

    with mock.patch(SEND_METHOD, side_effect=get_valid_response) as _:
        response = client.get(
            ENDPOINT_URL,
            query_string={
                "query": "query",
                "count": "10",
                "start": "5",
            },
        )

        assert response.status_code == 200

        data = response.get_json()

        assert 200 == data["code"]

        assert "title5" == data["feeds"][0]["title"]
        assert "title14" == data["feeds"][9]["title"]
        assert 10 == len(data["feeds"])


def test_paging_above_number_of_results(client) -> None:
    def get_valid_response(request: PreparedRequest, *args, **kwargs) -> Response:
        return podcastindex_mock.generate_limited_response(request, 5)

    with mock.patch(SEND_METHOD, side_effect=get_valid_response) as _:
        response = client.get(
            ENDPOINT_URL,
            query_string={
                "query": "query",
                "count": "10",
                "start": "10",
            },
        )

        assert response.status_code == 200

        data = response.get_json()

        assert 200 == data["code"]

        assert 0 == len(data["feeds"])


def test_default_count_is_25(client) -> None:
    def get_valid_response(request: PreparedRequest, *args, **kwargs) -> Response:
        return podcastindex_mock.generate_valid_response(request)

    with mock.patch(SEND_METHOD, side_effect=get_valid_response) as _:
        response = client.get(
            ENDPOINT_URL,
            query_string={
                "query": "query",
            },
        )

        assert response.status_code == 200

        data = response.get_json()

        assert 200 == data["code"]

        assert "title0" == data["feeds"][0]["title"]
        assert 25 == len(data["feeds"])


def test_returns_less_results_when_less_feeds_found(client) -> None:
    def get_limited_response(request: PreparedRequest, *args, **kwargs) -> Response:
        return podcastindex_mock.generate_limited_response(request, 5)

    with mock.patch(SEND_METHOD, side_effect=get_limited_response) as _:
        response = client.get(
            ENDPOINT_URL,
            query_string={
                "query": "query",
                "count": 10,
            },
        )

        assert response.status_code == 200

        data = response.get_json()

        assert 200 == data["code"]
        assert 5 == len(data["feeds"])


def test_returns_no_results_when_no_feeds_found(client) -> None:
    def get_limited_response(request: PreparedRequest, *args, **kwargs) -> Response:
        return podcastindex_mock.generate_limited_response(request, 0)

    with mock.patch(SEND_METHOD, side_effect=get_limited_response) as _:
        response = client.get(
            ENDPOINT_URL,
            query_string={
                "query": "query",
                "count": 10,
            },
        )

        assert response.status_code == 200

        data = response.get_json()

        assert 200 == data["code"]
        assert 0 == len(data["feeds"])


def test_returns_timeout_when_request_times_out(client) -> None:
    def return_timeout(request: PreparedRequest, *args, **kwargs) -> Response:
        raise exceptions.Timeout()

    with mock.patch(SEND_METHOD, side_effect=return_timeout) as _:
        response = client.get(
            ENDPOINT_URL, query_string={"query": "query", "count": "5"}
        )

        assert response.status_code == 504

        data = response.get_json()

        assert 504 == data["code"]

        assert "ExternalApiTimeout" == data["error"]


def test_returns_bad_response_when_api_responds_bad_request(client) -> None:
    def return_bad_request(request: PreparedRequest, *args, **kwargs) -> Response:
        return podcastindex_mock.generate_bad_request_response(request)

    with mock.patch(SEND_METHOD, side_effect=return_bad_request) as _:
        response = client.get(
            ENDPOINT_URL, query_string={"query": "query", "count": "5"}
        )

        assert response.status_code == 502

        data = response.get_json()

        assert 502 == data["code"]

        assert "ExternalApiBadResponse" == data["error"]


def test_returns_bad_response_when_api_responds_bad_authentication(client) -> None:
    def return_bad_authentication(
        request: PreparedRequest, *args, **kwargs
    ) -> Response:
        return podcastindex_mock.generate_bad_authentication_response(request)

    with mock.patch(SEND_METHOD, side_effect=return_bad_authentication) as _:
        response = client.get(
            ENDPOINT_URL, query_string={"query": "query", "count": "5"}
        )

        assert response.status_code == 502

        data = response.get_json()

        assert 502 == data["code"]

        assert "ExternalApiBadResponse" == data["error"]


def test_tolerates_extra_fields_from_response(client) -> None:
    def get_custom_response(request: PreparedRequest, *args, **kwargs) -> Response:
        def modifier(data: dict) -> dict:
            data["extra"] = "field"

        return podcastindex_mock.generate_custom_response(
            request,
            modifier,
        )

    with mock.patch(SEND_METHOD, side_effect=get_custom_response) as _:
        response = client.get(
            ENDPOINT_URL, query_string={"query": "query", "count": "5"}
        )

        assert response.status_code == 200

        data = response.get_json()

        assert 200 == data["code"]


def test_tolerates_empty_link(client) -> None:
    def get_custom_response(request: PreparedRequest, *args, **kwargs) -> Response:
        def modifier(data: dict) -> dict:
            data["feeds"][0]["link"] = ""

        return podcastindex_mock.generate_custom_response(
            request,
            modifier,
        )

    with mock.patch(SEND_METHOD, side_effect=get_custom_response) as _:
        response = client.get(
            ENDPOINT_URL, query_string={"query": "query", "count": "5"}
        )

        assert response.status_code == 200

        data = response.get_json()

        assert 200 == data["code"]


def test_returns_bad_response_when_expected_field_doesnt_fit_schema(client) -> None:
    def get_custom_response(request: PreparedRequest, *args, **kwargs) -> Response:
        def modifier(data: dict) -> dict:
            data["query"] = ""

        return podcastindex_mock.generate_custom_response(
            request,
            modifier,
        )

    with mock.patch(SEND_METHOD, side_effect=get_custom_response) as _:
        response = client.get(
            ENDPOINT_URL, query_string={"query": "query", "count": "5"}
        )

        assert response.status_code == 502

        data = response.get_json()

        assert 502 == data["code"]

        assert "ExternalApiBadResponse" == data["error"]


def test_feed_excluded_when_expected_feed_field_doesnt_fit_schema(client) -> None:
    def get_custom_response(request: PreparedRequest, *args, **kwargs) -> Response:
        def modifier(data: dict) -> dict:
            data["feeds"][0]["medium"] = "NonExistantMedium"

        return podcastindex_mock.generate_custom_response(
            request,
            modifier,
        )

    with mock.patch(SEND_METHOD, side_effect=get_custom_response) as _:
        response = client.get(
            ENDPOINT_URL, query_string={"query": "query", "count": "5"}
        )

        assert response.status_code == 200

        data = response.get_json()

        assert 200 == data["code"]

        # The invalid feed has title "title0".
        assert "title1" == data["feeds"][0]["title"]
