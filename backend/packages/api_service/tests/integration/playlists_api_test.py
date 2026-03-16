import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_login_required():
    with patch("rss_music_api_service.routes.auth.login_required", lambda x: x):
        yield


@pytest.fixture
def mock_user_id():
    with patch(
        "rss_music_api_service.routes.playlists.get_current_user_id", return_value="123"
    ):
        yield "123"


@pytest.fixture
def mock_db_service():
    with patch("rss_music_api_service.routes.playlists.db_service") as mock:
        yield mock


# --- CREATE PLAYLIST TESTS ---


def test_create_playlist_success(client, mock_user_id, mock_db_service):
    mock_db_service.create_playlist.return_value = {
        "id": 1,
        "title": "Synthwave Hits",
        "user_id": 123,
    }
    payload = {
        "title": "Synthwave Hits",
        "description": "High tempo neon vibes",
        "created_by_user_id": 123,
    }

    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 201
    assert response.json["title"] == "Synthwave Hits"
    mock_db_service.create_playlist.assert_called_once_with(
        title="Synthwave Hits", user_id=123, description="High tempo neon vibes"
    )


def test_create_playlist_missing_title(client, mock_user_id):
    payload = {"description": "No title here", "created_by_user_id": 123}

    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 400
    assert "title" in response.json["message"] or "title" in str(response.json)


def test_create_playlist_title_too_long(client, mock_user_id):
    long_title = "A" * 101
    payload = {"title": long_title, "created_by_user_id": 123}

    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 400
    assert "title" in response.json["message"]


# --- GET PLAYLIST TESTS ---


def test_get_user_playlists(client, mock_user_id, mock_db_service):
    mock_db_service.get_user_playlists.return_value = [
        {"id": 1, "title": "Lo-Fi Beats"},
        {"id": 2, "title": "Metal Mix"},
    ]

    response = client.get("/playlists/me")

    assert response.status_code == 200
    assert len(response.json["playlists"]) == 2
    assert response.json["playlists"][0]["title"] == "Lo-Fi Beats"
    mock_db_service.get_user_playlists.assert_called_once_with(123)


def test_get_user_playlists_empty(client, mock_user_id, mock_db_service):
    # Setup: Mock returns an empty list for a brand new user
    mock_db_service.get_user_playlists.return_value = []

    response = client.get("/playlists/me")

    assert response.status_code == 200
    assert response.json["playlists"] == []


def test_create_playlist_db_failure(client, mock_user_id, mock_db_service, app):
    mock_db_service.create_playlist.side_effect = Exception("Database is down")

    payload = {"title": "Testing Failure", "created_by_user_id": 123}

    app.config["PROPAGATE_EXCEPTIONS"] = False

    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 500


def test_create_playlist_malformed_json(client, mock_user_id):
    # Sending raw string data that is not valid JSON
    response = client.post(
        "/playlists/create",
        data='{"title": "Broken JSON"',  # Missing closing brace
        content_type="application/json",
    )

    assert response.status_code == 400


# --- UPDATE PLAYLIST TESTS ---


def test_update_playlist_success(client, mock_user_id, mock_db_service):
    mock_db_service.update_playlist.return_value = {
        "id": 5,
        "title": "New Title",
        "description": "Updated description",
    }
    payload = {
        "title": "New Title",
        "description": "Updated description",
        "created_by_user_id": 123,
    }

    response = client.put("/playlists/5", json=payload)

    assert response.status_code == 200
    assert response.json["title"] == "New Title"
    mock_db_service.update_playlist.assert_called_once_with(
        playlist_id=5, user_id=123, title="New Title", description="Updated description"
    )


def test_update_playlist_unauthorized_or_missing(client, mock_user_id, mock_db_service):
    mock_db_service.update_playlist.return_value = None

    response = client.put(
        "/playlists/999", json={"title": "Ghost Playlist", "created_by_user_id": 123}
    )

    assert response.status_code == 404
    assert "unauthorized" in response.json["message"]


# --- DELETE PLAYLIST TESTS ---


def test_delete_playlist_success(client, mock_user_id, mock_db_service):
    mock_db_service.delete_playlist.return_value = True

    response = client.delete("/playlists/10")

    assert response.status_code == 200
    assert "deleted successfully" in response.json["message"]
    mock_db_service.delete_playlist.assert_called_once_with(playlist_id=10, user_id=123)


def test_delete_playlist_fail(client, mock_user_id, mock_db_service):
    mock_db_service.delete_playlist.return_value = False

    response = client.delete("/playlists/88")

    assert response.status_code == 404
    mock_db_service.delete_playlist.assert_called_once_with(playlist_id=88, user_id=123)
