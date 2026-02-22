from rss_music_api_service.external_apis.concrete import PodcastIndexAPI

AUTHENTICATION_HEADERS = {"User-Agent", "X-Auth-Key", "X-Auth-Date", "Authorization"}


# Authentication Headers
def test_user_agent_in_headers() -> None:
    user_agent = "CoolMusicApp/1.0"

    headers = PodcastIndexAPI._create_auth_headers(user_agent, "key", "secret", 5)

    assert "User-Agent" in headers
    assert user_agent == headers["User-Agent"]


def test_api_key_in_headers() -> None:
    key = "API-key"

    headers = PodcastIndexAPI._create_auth_headers("App/1.0", key, "secret", 5)

    assert "X-Auth-Key" in headers
    assert key == headers["X-Auth-Key"]


def test_date_in_headers() -> None:
    date = 54321

    headers = PodcastIndexAPI._create_auth_headers("App/1.0", "key", "secret", date)

    assert "X-Auth-Date" in headers
    assert str(date) == headers["X-Auth-Date"]


def test_authentication_hash_in_headers() -> None:
    expected_hash = "e703eafbf4d6143009d5a308b1cc92a2c80f1e2e"

    headers = PodcastIndexAPI._create_auth_headers("App/1.0", "key", "secret", 5)

    assert "Authorization" in headers
    assert expected_hash == headers["Authorization"]


def test_secret_not_in_headers() -> None:
    secret = "API-secret"

    headers = PodcastIndexAPI._create_auth_headers("App/1.0", "key", secret, 5)

    for key, value in headers.items():
        assert secret not in value, f"API secret leaked in header: {key}"


# Feed Searching
def test_search_feed_request_http_method() -> None:
    expected = "GET"

    auth_headers = {key: "XXX-TEST-XXX" for key in AUTHENTICATION_HEADERS}
    request, context = PodcastIndexAPI._make_search_request(
        "query", 10, 5, auth_headers
    )

    assert expected == request.method


def test_search_feed_request_url_correct() -> None:
    expected_url = (
        "https://api.podcastindex.org/api/1.0/search/music/byterm?q=query&max=15"
    )

    auth_headers = {key: "XXX-TEST-XXX" for key in AUTHENTICATION_HEADERS}
    request, context = PodcastIndexAPI._make_search_request(
        "query", 10, 5, auth_headers
    )

    assert expected_url == request.url


def test_search_feed_request_includes_auth_headers() -> None:
    auth_headers = {key: "XXX-TEST-XXX" for key in AUTHENTICATION_HEADERS}
    request, context = PodcastIndexAPI._make_search_request(
        "query", 10, 5, auth_headers
    )

    for header in AUTHENTICATION_HEADERS:
        assert header in request.headers, (
            f"Authentication header '{header}' not found in request headers"
        )


def test_search_feed_context_matches_paging_args() -> None:
    auth_headers = {key: "XXX-TEST-XXX" for key in AUTHENTICATION_HEADERS}
    request, context = PodcastIndexAPI._make_search_request(
        "query", 8, 12, auth_headers
    )

    assert "start" in context
    assert "count" in context
    assert 8 == context["count"]
    assert 12 == context["start"]
