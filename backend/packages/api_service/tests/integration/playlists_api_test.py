import os
from requests.exceptions import Timeout
import json
from unittest.mock import patch

from helpers import ConstantResponse


# --- CREATE TESTS ---


def test_create_playlist_success(auth_client, user, custom_responses):
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/create"] = (
        ConstantResponse(
            status_code=201,
            json_data={"id": 1, "title": "Gym Mix", "created_by_user_id": user.id},
        )
    )

    payload = {
        "title": "Gym Mix",
        "description": "High energy",
    }
    # import pdb; pdb.set_trace()
    response = auth_client.post("/playlists/create", json=payload)

    assert response.status_code == 201
    assert response.json["title"] == "Gym Mix"


def test_create_playlist_validation_error(auth_client):
    payload = {"description": "Missing title field"}
    response = auth_client.post("/playlists/create", json=payload)

    assert response.status_code == 400
    assert response.json["error"] == "InvalidArgument"


def test_create_playlist_enforces_auth_user_id(auth_client, user, custom_responses):
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/create"] = (
        ConstantResponse(
            status_code=201,
            json_data={"id": 1, "title": "Gym Mix", "created_by_user_id": user.id},
        )
    )

    payload = {"title": "My Playlist"}
    auth_client.post("/playlists/create", json=payload)

    sent_request = custom_responses["_requests"][-1]
    sent_body = json.loads(sent_request.body)
    assert sent_body["created_by_user_id"] == user.id


def test_create_playlist_without_description(auth_client, user, custom_responses):
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/create"] = (
        ConstantResponse(
            status_code=201,
            json_data={
                "id": 1,
                "title": "No Description Mix",
                "created_by_user_id": user.id,
            },
        )
    )

    payload = {
        "title": "No Description Mix",
    }
    response = auth_client.post("/playlists/create", json=payload)

    assert response.status_code == 201
    assert response.json["title"] == "No Description Mix"

    sent_request = custom_responses["_requests"][0]
    sent_body = json.loads(sent_request.body)
    assert "description" not in sent_body


# --- GET TESTS ---


def test_get_user_playlists_success(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/user/{user.id}"
    ] = ConstantResponse(
        status_code=200,
        json_data=[{"id": 1, "title": "Lo-Fi"}],
    )

    response = auth_client.get("/playlists/me")

    assert response.status_code == 200
    assert len(response.json["playlists"]) == 1


# --- UPDATE TESTS ---


def test_update_playlist_success(auth_client, custom_responses):
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/5"] = (
        ConstantResponse(
            status_code=200,
            json_data={
                "id": 5,
                "title": "Updated",
                "track_count": 0,
                "updated_at": "2026-03-18T23:05:48.654349",
            },
        )
    )

    payload = {"title": "Updated", "description": "New"}
    response = auth_client.put("/playlists/5", json=payload)

    assert response.status_code == 200
    assert response.json["title"] == "Updated"


def test_update_playlist_not_found(auth_client, custom_responses):
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/999"] = (
        ConstantResponse(
            status_code=404,
            json_data={"error": "NotFound", "message": "Missing"},
        )
    )

    response = auth_client.put("/playlists/999", json={"title": "Doesn't Exist"})

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"


def test_update_playlist_timeout(auth_client, custom_responses):
    def timeout(_request):
        raise Timeout()

    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/5"] = timeout

    payload = {"title": "Updated", "description": "New"}

    response = auth_client.put("/playlists/5", json=payload)

    assert response.status_code == 504
    assert response.json["error"] == "InternalApiTimeout"


# --- DELETE TESTS ---


def test_delete_playlist_success(auth_client, custom_responses):
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/10"] = (
        ConstantResponse(
            status_code=200,
            json_data={"message": "Deleted"},
        )
    )

    response = auth_client.delete("/playlists/10")

    assert response.status_code == 200
    assert response.json["message"] == "Playlist deleted successfully"


def test_delete_playlist_not_found(auth_client, custom_responses):
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/999"] = (
        ConstantResponse(
            status_code=404,
            json_data={"error": "NotFound", "message": "Missing"},
        )
    )

    response = auth_client.delete("/playlists/999")

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"


# --- GET /playlists/<id> tests ---


@patch("rss_music_api_service.routes.playlists.LinkFunctions.get_feed_by_url")
def test_get_playlist_success(mock_get_feed, auth_client, user, custom_responses):
    from rss_music_api_service.data import Rss

    mock_get_feed.return_value = Rss(
        url="http://example.com/feed.rss",
        title="Test Podcast",
        description="A test podcast",
        artist="Test Artist",
        link="http://example.com",
        art_url="http://example.com/art.jpg",
        language="en",
        pub_date="",
        last_build_date="",
        items=[{"enclosure_url": "http://example.com/ep1.mp3", "title": "Ep 1"}],
        value_items=[{}],
    )

    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/5"] = (
        ConstantResponse(
            status_code=200,
            json_data={
                "id": 5,
                "title": "Car",
                "description": "Road tunes",
                "track_count": 1,
                "created_by_user_id": user.id,
                "created_at": "2026-01-01T00:00:00",
                "tracks": [
                    {
                        "id": 1,
                        "playlist_id": 5,
                        "track_url": "http://example.com/feed.rss",
                        "position": 1,
                        "added_at": "2026-01-01T00:00:00",
                    }
                ],
            },
        )
    )

    response = auth_client.get("/playlists/5")

    assert response.status_code == 200
    data = response.json
    assert data["title"] == "Car"
    assert len(data["tracks"]) == 1
    assert data["tracks"][0]["title"] == "Test Podcast"
    assert data["tracks"][0]["artist"] == "Test Artist"
    assert data["tracks"][0]["audio"] == "http://example.com/ep1.mp3"


def test_get_playlist_not_found(auth_client, custom_responses):
    custom_responses[f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/999"] = (
        ConstantResponse(
            status_code=404,
            json_data={"error": "NotFound", "message": "Missing"},
        )
    )

    response = auth_client.get("/playlists/999")

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"


def test_get_playlist_requires_auth(client, custom_responses):
    response = client.get("/playlists/5")
    assert response.status_code == 401


# --- POST /playlists/<id>/tracks/add tests ---


def test_add_track_success(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/5/tracks/add"
    ] = ConstantResponse(
        status_code=201,
        json_data={
            "id": 1,
            "playlist_id": 5,
            "track_url": "http://example.com/feed.rss",
            "position": 1,
            "added_at": "2026-01-01T00:00:00",
        },
    )

    response = auth_client.post(
        "/playlists/5/tracks/add", json={"track_url": "http://example.com/feed.rss"}
    )

    assert response.status_code == 201
    assert response.json["track_url"] == "http://example.com/feed.rss"
    assert response.json["position"] == 1


def test_add_track_sends_user_id(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/5/tracks/add"
    ] = ConstantResponse(
        status_code=201,
        json_data={
            "id": 1,
            "playlist_id": 5,
            "track_url": "http://example.com/feed.rss",
            "position": 1,
            "added_at": "2026-01-01T00:00:00",
        },
    )

    auth_client.post(
        "/playlists/5/tracks/add", json={"track_url": "http://example.com/feed.rss"}
    )

    sent_body = json.loads(custom_responses["_requests"][-1].body)
    assert sent_body["created_by_user_id"] == user.id


def test_add_track_validation_error(auth_client):
    response = auth_client.post("/playlists/5/tracks/add", json={})

    assert response.status_code == 400
    assert response.json["error"] == "InvalidArgument"


def test_add_track_not_found(auth_client, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/999/tracks/add"
    ] = ConstantResponse(
        status_code=404,
        json_data={"error": "NotFound", "message": "Missing"},
    )

    response = auth_client.post(
        "/playlists/999/tracks/add", json={"track_url": "http://example.com/feed.rss"}
    )

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"


# --- DELETE /playlists/<id>/tracks/remove tests ---


def test_remove_track_success(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/5/tracks/remove"
    ] = ConstantResponse(
        status_code=200,
        json_data={"message": "Track removed", "playlist_track_id": 1},
    )

    response = auth_client.delete(
        "/playlists/5/tracks/remove",
        json={"track_url": "http://example.com/feed.rss"},
    )

    assert response.status_code == 200
    assert response.json["message"] == "Track removed"


def test_remove_track_not_found(auth_client, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/5/tracks/remove"
    ] = ConstantResponse(
        status_code=404,
        json_data={"error": "NotFound", "message": "Missing"},
    )

    response = auth_client.delete(
        "/playlists/5/tracks/remove",
        json={"track_url": "http://example.com/missing.rss"},
    )

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"


def test_remove_track_validation_error(auth_client):
    response = auth_client.delete("/playlists/5/tracks/remove", json={})

    assert response.status_code == 400
    assert response.json["error"] == "InvalidArgument"


# --- PATCH /playlists/<id>/tracks/reorder tests ---


def test_reorder_track_success(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/5/tracks/reorder"
    ] = ConstantResponse(
        status_code=200,
        json_data={
            "id": 1,
            "playlist_id": 5,
            "track_url": "http://example.com/feed.rss",
            "position": 3,
            "added_at": "2026-01-01T00:00:00",
        },
    )

    response = auth_client.patch(
        "/playlists/5/tracks/reorder",
        json={"track_url": "http://example.com/feed.rss", "new_position": 3},
    )

    assert response.status_code == 200
    assert response.json["position"] == 3


def test_reorder_track_sends_user_id(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/5/tracks/reorder"
    ] = ConstantResponse(
        status_code=200,
        json_data={
            "id": 1,
            "playlist_id": 5,
            "track_url": "http://example.com/feed.rss",
            "position": 2,
            "added_at": "2026-01-01T00:00:00",
        },
    )

    auth_client.patch(
        "/playlists/5/tracks/reorder",
        json={"track_url": "http://example.com/feed.rss", "new_position": 2},
    )

    sent_body = json.loads(custom_responses["_requests"][-1].body)
    assert sent_body["created_by_user_id"] == user.id


def test_reorder_track_validation_error(auth_client):
    response = auth_client.patch("/playlists/5/tracks/reorder", json={})

    assert response.status_code == 400
    assert response.json["error"] == "InvalidArgument"


def test_reorder_track_not_found(auth_client, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/playlists/5/tracks/reorder"
    ] = ConstantResponse(
        status_code=404,
        json_data={"error": "NotFound", "message": "Missing"},
    )

    response = auth_client.patch(
        "/playlists/5/tracks/reorder",
        json={"track_url": "http://example.com/missing.rss", "new_position": 1},
    )

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"
