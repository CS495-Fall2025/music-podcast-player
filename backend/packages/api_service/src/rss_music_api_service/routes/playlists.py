from flask import Blueprint, request
from rss_music_api_service.internal_apis import db_service
from rss_music_api_service.routes.auth import login_required
from rss_music_api_service.auth.current_user import get_current_user_id
from rss_music_db_service_schemas.playlists import requests as playlist_reqs

PLAYLISTS_BP = Blueprint("playlists", __name__)

# Create playlist


@PLAYLISTS_BP.post("/create")
@login_required
def create_playlist():
    user_id = get_current_user_id()

    payload = request.get_json(silent=True) or {}
    payload["created_by_user_id"] = int(user_id)
    request_data = playlist_reqs.CreatePlaylistRequest().load(payload)

    result = db_service.create_playlist(
        title=request_data["title"],
        user_id=user_id,
        description=request_data.get("description"),
    )
    return result, 201


# Get user playlists


@PLAYLISTS_BP.get("/user/<int:user_id>")
@login_required  # Ensure the requester is logged in
def get_user_playlists(user_id):
    # Security: Verify the requester IS the user in the URL
    if get_current_user_id() != user_id:
        return {
            "error": "Forbidden",
            "message": "You cannot view other users' playlists.",
        }, 403

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

    # Pass the ID from the URL and the user_id for security
    result = db_service.update_playlist(
        playlist_id=id,
        user_id=user_id,
        title=request_data.get("title"),
        description=request_data.get("description"),
    )
    return result, 200


# Delete playlist


@PLAYLISTS_BP.delete("/<int:id>")
@login_required
def delete_playlist(id):
    user_id = get_current_user_id()

    db_service.delete_playlist(playlist_id=id, user_id=user_id)

    return {"message": "Playlist deleted successfully"}, 200
