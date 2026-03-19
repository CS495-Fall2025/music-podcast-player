import pytest
from unittest import mock
import requests
import json

SEND_METHOD = "requests.Session.send"


@pytest.fixture
def mock_db_response():
    """Intercepts outgoing DB requests and returns a custom response."""
    with mock.patch(SEND_METHOD) as mocked_send:

        def _set_response(status_code: int, json_data: dict):
            mock_res = requests.Response()
            mock_res.status_code = status_code
            mock_res._content = json.dumps(json_data).encode("utf-8")
            mock_res.headers["Content-Type"] = "application/json"
            mocked_send.return_value = mock_res
            return mocked_send

        yield _set_response


@pytest.fixture
def mock_user_id():
    """Mocks the authentication check to return a consistent User ID."""
    user_id = 123
    with mock.patch(
        "rss_music_api_service.routes.auth.get_current_user_id", return_value=user_id
    ):
        with mock.patch(
            "rss_music_api_service.routes.playlists.get_current_user_id",
            return_value=user_id,
        ):
            yield user_id


# --- CREATE TESTS ---


def test_create_playlist_success(client, mock_user_id, mock_db_response):
    mock_db_response(
        status_code=201,
        json_data={"id": 1, "title": "Gym Mix",
                   "created_by_user_id": mock_user_id},
    )

    payload = {
        "title": "Gym Mix",
        "description": "High energy",
        "created_by_user_id": mock_user_id,
    }
    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 201
    assert response.json["title"] == "Gym Mix"


def test_create_playlist_validation_error(client, mock_user_id):
    payload = {"description": "Missing title field"}
    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 400
    assert response.json["error"] == "InvalidArgument"


def test_create_playlist_enforces_auth_user_id(client, mock_user_id, mock_db_response):
    mock_send = mock_db_response(status_code=201, json_data={"id": 1})

    payload = {"title": "My Playlist", "created_by_user_id": 999}
    client.post("/playlists/create", json=payload)

    sent_request = mock_send.call_args[0][0]
    sent_body = json.loads(sent_request.body)
    assert sent_body["created_by_user_id"] == mock_user_id


def test_create_playlist_without_description(client, mock_user_id, mock_db_response):
    mock_send = mock_db_response(
        status_code=201,
        json_data={"id": 1, "title": "No Description Mix",
                   "created_by_user_id": mock_user_id},
    )

    payload = {
        "title": "No Description Mix",
        "created_by_user_id": mock_user_id,
    }
    response = client.post("/playlists/create", json=payload)

    assert response.status_code == 201
    assert response.json["title"] == "No Description Mix"

    sent_request = mock_send.call_args[0][0]
    sent_body = json.loads(sent_request.body)
    assert "description" not in sent_body


# --- GET TESTS ---


def test_get_user_playlists_success(client, mock_user_id, mock_db_response):
    mock_db_response(status_code=200, json_data=[{"id": 1, "title": "Lo-Fi"}])

    response = client.get("/playlists/me")

    assert response.status_code == 200
    assert len(response.json["playlists"]) == 1


# --- UPDATE TESTS ---


def test_update_playlist_success(client, mock_user_id, mock_db_response):
    mock_db_response(
        status_code=200,
        json_data={"id": 5,
                   "title": "Updated",
                   "track_count": 0,
                   "updated_at": "2026-03-18T23:05:48.654349"},
    )

    payload = {"title": "Updated", "description": "New",
               "created_by_user_id": mock_user_id}
    response = client.put("/playlists/5", json=payload)

    assert response.status_code == 200
    assert response.json["title"] == "Updated"


def test_update_playlist_not_found(client, mock_user_id, mock_db_response):
    mock_db_response(
        status_code=404, json_data={"error": "NotFound", "message": "Missing"}
    )

    response = client.put(
        "/playlists/999", json={"title": "Doesn't Exist", "created_by_user_id": mock_user_id}
    )

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"


# --- DELETE TESTS ---


def test_delete_playlist_success(client, mock_user_id, mock_db_response):
    mock_db_response(status_code=200, json_data={"message": "Deleted"})

    response = client.delete("/playlists/10")

    assert response.status_code == 200
    assert response.json["message"] == "Playlist deleted successfully"


def test_delete_playlist_not_found(client, mock_user_id, mock_db_response):
    mock_db_response(
        status_code=404, json_data={"error": "NotFound", "message": "Missing"}
    )

    response = client.delete("/playlists/999")

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"
