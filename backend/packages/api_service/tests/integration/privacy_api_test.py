import os

from helpers import ConstantResponse


# --- GET /playlists/me/privacy ---


def test_get_privacy_success(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/{user.id}/privacy"
    ] = ConstantResponse(status_code=200, json_data={"profile_public": True})

    response = auth_client.get("/playlists/me/privacy")

    assert response.status_code == 200
    assert response.json["profile_public"] is True


def test_get_privacy_returns_false_when_private(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/{user.id}/privacy"
    ] = ConstantResponse(status_code=200, json_data={"profile_public": False})

    response = auth_client.get("/playlists/me/privacy")

    assert response.status_code == 200
    assert response.json["profile_public"] is False


def test_get_privacy_requires_auth(client, custom_responses):
    response = client.get("/playlists/me/privacy")

    assert response.status_code == 401


# --- PATCH /playlists/me/privacy ---


def test_patch_privacy_set_to_false(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/{user.id}/privacy"
    ] = ConstantResponse(status_code=200, json_data={"profile_public": False})

    response = auth_client.patch(
        "/playlists/me/privacy", json={"profile_public": False}
    )

    assert response.status_code == 200
    assert response.json["profile_public"] is False


def test_patch_privacy_set_to_true(auth_client, user, custom_responses):
    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/{user.id}/privacy"
    ] = ConstantResponse(status_code=200, json_data={"profile_public": True})

    response = auth_client.patch("/playlists/me/privacy", json={"profile_public": True})

    assert response.status_code == 200
    assert response.json["profile_public"] is True


def test_patch_privacy_rejects_non_boolean(auth_client):
    response = auth_client.patch(
        "/playlists/me/privacy", json={"profile_public": "yes"}
    )

    assert response.status_code == 400
    assert response.json["error"] == "InvalidArgument"


def test_patch_privacy_rejects_missing_field(auth_client):
    response = auth_client.patch("/playlists/me/privacy", json={})

    assert response.status_code == 400
    assert response.json["error"] == "InvalidArgument"


def test_patch_privacy_requires_auth(client, custom_responses):
    response = client.patch("/playlists/me/privacy", json={"profile_public": False})

    assert response.status_code == 401


def test_patch_privacy_sends_correct_user_id(auth_client, user, custom_responses):
    import json

    custom_responses[
        f"{os.environ['RSS_PLAYER_DB_SERVICE_URL']}/users/{user.id}/privacy"
    ] = ConstantResponse(status_code=200, json_data={"profile_public": False})

    auth_client.patch("/playlists/me/privacy", json={"profile_public": False})

    sent_request = custom_responses["_requests"][-1]
    assert f"/users/{user.id}/privacy" in sent_request.url
    sent_body = json.loads(sent_request.body)
    assert sent_body["profile_public"] is False
