from rss_music_backend.external_apis.concrete import PodcastIndexAPI


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
