import pytest
from unittest import mock


@pytest.fixture
def mock_db_service():
    with mock.patch("rss_music_api_service.routes.playlists.db_service") as mocked:
        yield mocked


@pytest.fixture
def mock_user_id():
    user_id = 123
    with mock.patch(
        "rss_music_api_service.routes.auth.get_current_user_id", return_value=user_id
    ):
        with mock.patch(
            "rss_music_api_service.routes.playlists.get_current_user_id",
            return_value=user_id,
        ):
            yield user_id


# --- PLAYLIST TESTS ---


def test_create_playlist_success(client, mock_user_id, mock_db_service):
    mock_db_service.create_playlist.return_value = {
        "id": 1,
        "title": "Gym Mix",
        "user_id": 123,
    }

    payload = {
        "title": "Gym Mix",
        "description": "High energy",
        "created_by_user_id": 123,
    }
    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 201
    assert response.json["title"] == "Gym Mix"
    mock_db_service.create_playlist.assert_called_once()


def test_get_user_playlists(client, mock_user_id, mock_db_service):
    mock_db_service.get_user_playlists.return_value = [
        {"id": 1, "title": "Lo-Fi"}]

    response = client.get("/playlists/me")

    assert response.status_code == 200
    mock_db_service.get_user_playlists.assert_called_once_with(123)


def test_update_playlist_success(client, mock_user_id, mock_db_service):
    mock_db_service.update_playlist.return_value = {
        "id": 5,
        "title": "Updated",
        "description": "New",
    }

    response = client.put(
        "/playlists/5",
        json={"title": "Updated", "description": "New",
              "created_by_user_id": 123},
    )

    assert response.status_code == 200
    mock_db_service.update_playlist.assert_called_once()


def test_delete_playlist_success(client, mock_user_id, mock_db_service):
    mock_db_service.delete_playlist.return_value = True

    response = client.delete("/playlists/10")

    assert response.status_code == 200
    mock_db_service.delete_playlist.assert_called_once_with(
        playlist_id=10, user_id=123)
