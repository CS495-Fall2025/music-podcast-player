import os
import pytest
from unittest import mock
import requests
from requests.exceptions import Timeout
import json

from helpers import ConstantResponse


# --- CREATE TESTS ---


def test_create_playlist_success(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/playlists/create"
    ] = ConstantResponse(
        status_code=201,
        json_data={"id": 1, "title": "Gym Mix", "created_by_user_id": user.id},
    )

    payload = {
        "title": "Gym Mix",
        "description": "High energy",
    }
    #import pdb; pdb.set_trace()
    response = auth_client.post("/playlists/create", json=payload)

    assert response.status_code == 201
    assert response.json["title"] == "Gym Mix"


def test_create_playlist_validation_error(auth_client):
    payload = {"description": "Missing title field"}
    response = auth_client.post("/playlists/create", json=payload)

    assert response.status_code == 400
    assert response.json["error"] == "InvalidArgument"


def test_create_playlist_enforces_auth_user_id(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/playlists/create"
    ] = ConstantResponse(
        status_code=201,
        json_data={"id": 1, "title": "Gym Mix", "created_by_user_id": user.id},
    )

    payload = {"title": "My Playlist"}
    auth_client.post("/playlists/create", json=payload)

    sent_request = custom_responses["_requests"][-1]
    sent_body = json.loads(sent_request.body)
    assert sent_body["created_by_user_id"] == user.id


def test_create_playlist_without_description(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/playlists/create"
    ] = ConstantResponse(
        status_code=201,
        json_data={
            "id": 1,
            "title": "No Description Mix",
            "created_by_user_id": user.id,
        },
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
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/playlists/user/{user.id}"
    ] = ConstantResponse(
        status_code=200,
        json_data=[{"id": 1, "title": "Lo-Fi"}],
    )

    response = auth_client.get("/playlists/me")

    assert response.status_code == 200
    assert len(response.json["playlists"]) == 1


# --- UPDATE TESTS ---


def test_update_playlist_success(auth_client, custom_responses):
    custom_responses[
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/playlists/5"
    ] = ConstantResponse(
        status_code=200,
        json_data={
            "id": 5,
            "title": "Updated",
            "track_count": 0,
            "updated_at": "2026-03-18T23:05:48.654349",
        },
    )

    payload = {"title": "Updated", "description": "New"}
    response = auth_client.put("/playlists/5", json=payload)

    assert response.status_code == 200
    assert response.json["title"] == "Updated"


def test_update_playlist_not_found(auth_client, custom_responses):
    custom_responses[
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/playlists/999"
    ] = ConstantResponse(
        status_code=404,
        json_data={"error": "NotFound", "message": "Missing"},
    )

    response = auth_client.put("/playlists/999", json={"title": "Doesn't Exist"})

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"


def test_update_playlist_timeout(auth_client, custom_responses):
    def timeout(_request):
        raise Timeout()

    custom_responses[
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/playlists/5"
    ] = timeout

    payload = {"title": "Updated", "description": "New"}

    response = auth_client.put("/playlists/5", json=payload)

    assert response.status_code == 504
    assert response.json["error"] == "InternalApiTimeout"


# --- DELETE TESTS ---


def test_delete_playlist_success(auth_client, custom_responses):
    custom_responses[
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/playlists/10"
    ] = ConstantResponse(
        status_code=200,
        json_data={"message": "Deleted"},
    )

    response = auth_client.delete("/playlists/10")

    assert response.status_code == 200
    assert response.json["message"] == "Playlist deleted successfully"


def test_delete_playlist_not_found(auth_client, custom_responses):
    custom_responses[
        f"{os.environ["RSS_PLAYER_DB_SERVICE_URL"]}/playlists/999"
    ] = ConstantResponse(
        status_code=404,
        json_data={"error": "NotFound", "message": "Missing"},
    )

    response = auth_client.delete("/playlists/999")

    assert response.status_code == 404
    assert response.json["error"] == "NotFound"
