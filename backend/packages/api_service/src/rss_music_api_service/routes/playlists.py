from flask import Blueprint, request
from marshmallow import ValidationError
from rss_music_api_service.internal_apis import db_service
from rss_music_api_service.routes.auth import login_required
from rss_music_api_service.auth.current_user import get_current_user_id
from rss_music_db_service_schemas.playlists import requests as playlist_reqs
from rss_music_db_service_schemas.playlists import responses as playlist_resps
from rss_music_api_service.errors import RequestError, get_error_response
from rss_music_api_service.internal_apis import errors as db_errors

PLAYLISTS_BP = Blueprint("playlists", __name__, url_prefix="/playlists")

# Create playlist


@PLAYLISTS_BP.post("/create")
@login_required
def create_playlist():
    user_id = int(get_current_user_id())
    payload = request.get_json(silent=True) or {}

    try:
        request_data = playlist_reqs.CreatePlaylistRequest(
            exclude=("created_by_user_id",)
        ).load(payload)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    create_kwargs = {"title": request_data["title"], "user_id": user_id}

    if request_data.get("description") is not None:
        create_kwargs["description"] = request_data["description"]

    try:
        result = db_service.create_playlist(**create_kwargs)
        return result, 201
    except db_errors.InternalAPINotFoundError:
        return get_error_response(RequestError.NOT_FOUND)
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)


# Get user playlists


@PLAYLISTS_BP.get("/me")
@login_required
def get_user_playlists():
    user_id = int(get_current_user_id())
    result = db_service.get_user_playlists(user_id)
    return {"playlists": result}, 200


# Update playlist


@PLAYLISTS_BP.put("/<int:id>")
@login_required
def update_playlist(id):
    user_id = int(get_current_user_id())
    payload = request.get_json(silent=True) or {}

    try:
        request_data = playlist_reqs.UpdatePlaylistRequest(
            exclude=("created_by_user_id",)
        ).load(payload)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    update_kwargs = {
        "playlist_id": id,
        "user_id": user_id,
        "title": request_data.get("title"),
        "description": request_data.get("description"),
    }

    try:
        updated_playlist = db_service.update_playlist(**update_kwargs)
        return playlist_resps.UpdatePlaylistResponse().dump(updated_playlist)
    except db_errors.InternalAPINotFoundError:
        return get_error_response(RequestError.NOT_FOUND)
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)


# Delete playlist


@PLAYLISTS_BP.delete("/<int:id>")
@login_required
def delete_playlist(id):
    user_id = int(get_current_user_id())

    try:
        db_service.delete_playlist(playlist_id=id, user_id=user_id)
        return {"message": "Playlist deleted successfully"}, 200
    except db_errors.InternalAPINotFoundError:
        return get_error_response(RequestError.NOT_FOUND)
    except db_errors.InternalAPIBadResponseError:
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)
    except db_errors.InternalAPITransportError:
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)
