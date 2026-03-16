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

# --- Create ---


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


def test_create_playlist_validation_error(client, mock_user_id, mock_db_service):
    # Intentional bad payload: missing 'title'
    payload = {"description": "Missing title field", "created_by_user_id": 123}

    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 400
    assert response.json["error"] == "Validation error"
    assert "title" in response.json["message"]


def test_create_playlist_with_extra_fields(client, mock_user_id, mock_db_service):
    payload = {
        "title": "Valid Title",
        "created_by_user_id": 123,
        "hacker_field": "trying to inject data",
    }

    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 400
    assert "hacker_field" in response.json["message"]

    mock_db_service.create_playlist.assert_not_called()


def test_create_playlist_enforces_auth_user_id(client, mock_user_id, mock_db_service):
    mock_db_service.create_playlist.return_value = {
        "id": 1,
        "title": "Test",
        "user_id": 123,
    }

    payload = {"title": "My Playlist", "created_by_user_id": 999}

    client.post("/playlists/create", json=payload)

    args, kwargs = mock_db_service.create_playlist.call_args
    assert kwargs["user_id"] == 123


# --- Get ---


def test_get_user_playlists(client, mock_user_id, mock_db_service):
    mock_db_service.get_user_playlists.return_value = [{"id": 1, "title": "Lo-Fi"}]

    response = client.get("/playlists/me")

    assert response.status_code == 200
    mock_db_service.get_user_playlists.assert_called_once_with(123)


def test_get_playlists_no_auth(client, mock_db_service):
    with mock.patch(
        "rss_music_api_service.routes.auth.get_current_user_id", return_value=None
    ):
        response = client.get("/playlists/me")

    assert response.status_code == 401
    assert response.json["error"] == "MissingToken"


def test_playlist_route_invalid_id_type(client, mock_user_id):
    response = client.get("/playlists/abc")
    assert response.status_code == 404


# --- Update ---


def test_update_playlist_success(client, mock_user_id, mock_db_service):
    mock_db_service.update_playlist.return_value = {
        "id": 5,
        "title": "Updated",
        "description": "New",
    }

    response = client.put(
        "/playlists/5",
        json={"title": "Updated", "description": "New", "created_by_user_id": 123},
    )

    assert response.status_code == 200
    mock_db_service.update_playlist.assert_called_once()


def test_update_playlist_not_found(client, mock_user_id, mock_db_service):
    mock_db_service.update_playlist.return_value = None

    payload = {"title": "Non-existent", "created_by_user_id": 123}
    response = client.put("/playlists/999", json=payload)

    assert response.status_code == 404
    assert response.json["error"] == "Not Found"
    assert "unauthorized" in response.json["message"]


def test_update_playlist_partial_data(client, mock_user_id, mock_db_service):
    mock_db_service.update_playlist.return_value = {
        "id": 5,
        "title": "Only Title Updated",
    }

    payload = {"title": "Only Title Updated", "created_by_user_id": 123}

    response = client.put("/playlists/5", json=payload)

    assert response.status_code == 200
    args, kwargs = mock_db_service.update_playlist.call_args
    assert "description" not in kwargs


# --- Delete ---


def test_delete_playlist_success(client, mock_user_id, mock_db_service):
    mock_db_service.delete_playlist.return_value = True

    response = client.delete("/playlists/10")

    assert response.status_code == 200
    mock_db_service.delete_playlist.assert_called_once_with(playlist_id=10, user_id=123)


def test_delete_playlist_not_found(client, mock_user_id, mock_db_service):
    mock_db_service.delete_playlist.return_value = False

    response = client.delete("/playlists/999")

    assert response.status_code == 404
    assert response.json["error"] == "Not Found"


# --- Composition ---


def test_create_and_update_workflow(client, mock_user_id, mock_db_service):
    mock_db_service.create_playlist.return_value = {
        "id": 50,
        "title": "Original Title",
        "user_id": 123,
    }

    create_payload = {"title": "Original Title", "created_by_user_id": 123}
    create_res = client.post("/playlists/create", json=create_payload)
    playlist_id = create_res.json["id"]

    mock_db_service.update_playlist.return_value = {
        "id": 50,
        "title": "Updated Title",
        "user_id": 123,
    }

    update_payload = {"title": "Updated Title", "created_by_user_id": 123}
    update_res = client.put(f"/playlists/{playlist_id}", json=update_payload)

    assert update_res.status_code == 200
    assert update_res.json["title"] == "Updated Title"
