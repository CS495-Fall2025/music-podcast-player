from flask import Blueprint, request
from rss_music_api_service.internal_apis import db_service
from rss_music_api_service.routes.auth import login_required
from rss_music_api_service.auth.current_user import get_current_user_id
from rss_music_db_service_schemas.playlists import requests as playlist_reqs

PLAYLISTS_BP = Blueprint("playlists", __name__, url_prefix="/playlists")

# Create playlist


@PLAYLISTS_BP.post("/create")
@login_required
def create_playlist():
    user_id = get_current_user_id()
    payload = request.get_json(silent=True) or {}

    payload["created_by_user_id"] = int(user_id)
    request_data = playlist_reqs.CreatePlaylistRequest().load(payload)

    create_kwargs = {
        "title": request_data["title"],
        "user_id": user_id
    }

    if request_data.get("description") is not None:
        create_kwargs["description"] = request_data["description"]

    result = db_service.create_playlist(**create_kwargs)
    return result, 201


# Get user playlists


@PLAYLISTS_BP.get("/me")
@login_required  # Ensure the requester is logged in
def get_user_playlists():
    user_id = get_current_user_id()
    result = db_service.get_user_playlists(user_id)
    return {"playlists": result}, 200

# Update playlist


@PLAYLISTS_BP.put("/<int:id>")
@login_required
def update_playlist(id):
    # Load the update data (title/description)
    user_id = get_current_user_id()
    payload = request.get_json(silent=True) or {}
    payload["created_by_user_id"] = int(user_id)
    request_data = playlist_reqs.UpdatePlaylistRequest().load(payload)

    update_kwargs = {
        "playlist_id": id,
        "user_id": user_id,
        "title": request_data.get("title")
    }

    if request_data.get("description") is not None:
        update_kwargs["description"] = request_data["description"]

    # Pass the ID from the URL and the user_id for security
    updated_playlist = db_service.update_playlist(**update_kwargs)

    if updated_playlist is None:
        return {"error": "Not Found",
                "message": "Playlist not found or unauthorized"
                }, 404
    return playlist_reqs.UpdatePlaylistResponse().dump(updated_playlist), 200


# Delete playlist


@PLAYLISTS_BP.delete("/<int:id>")
@login_required
def delete_playlist(id):
    user_id = int(get_current_user_id())

    success = db_service.delete_playlist(playlist_id=id, user_id=user_id)

    if not success:
        return {"error": "Not Found",
                "message": "Playlist not found or unauthorized"
                }, 404

    return {"message": "Playlist deleted successfully"}, 200
