from flask import Blueprint, request
from marshmallow import ValidationError
from rss_music_api_service.internal_apis import db_service
from rss_music_api_service.routes.auth import login_required
from rss_music_api_service.auth.current_user import get_current_user_id
from rss_music_db_service_schemas.playlists import requests as playlist_reqs
from rss_music_db_service_schemas.playlists import responses as playlist_resps
from rss_music_db_service_schemas.playlist_tracks import requests as track_reqs
from rss_music_api_service.errors import RequestError, get_error_response
from rss_music_api_service.internal_apis import errors as db_errors
from rss_music_api_service.external_apis.concrete import LinkFunctions
from rss_music_api_service.external_apis.errors import ExternalAPIError

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


# Privacy settings


@PLAYLISTS_BP.get("/me/privacy")
@login_required
def get_privacy():
    user_id = int(get_current_user_id())
    profile_public = db_service.get_user_privacy(user_id)
    return {"profile_public": profile_public}, 200


@PLAYLISTS_BP.patch("/me/privacy")
@login_required
def update_privacy():
    user_id = int(get_current_user_id())
    payload = request.get_json(silent=True) or {}
    profile_public = payload.get("profile_public")
    if not isinstance(profile_public, bool):
        return get_error_response(RequestError.INVALID_ARGUMENT)
    db_service.set_user_privacy(user_id, profile_public)
    return {"profile_public": profile_public}, 200


# Public: get playlists by username (no auth required)


@PLAYLISTS_BP.get("/user/<string:username>")
def get_public_user_playlists(username):
    try:
        result = db_service.get_playlists_by_username(username)
        return {"playlists": result, "username": username}, 200
    except db_errors.InternalAPINotFoundError:
        return get_error_response(RequestError.NOT_FOUND)
    except db_errors.InternalAPIForbiddenError:
        return get_error_response(RequestError.NOT_FOUND)


# Public: get playlist by ID with enriched tracks (no auth required)


@PLAYLISTS_BP.get("/public/<int:id>")
def get_public_playlist(id):
    try:
        playlist = db_service.get_playlist(playlist_id=id)
    except db_errors.InternalAPINotFoundError:
        return get_error_response(RequestError.NOT_FOUND)

    playlist["tracks"] = _enrich_tracks(playlist.get("tracks", []))
    return playlist, 200


# Get playlist by ID (with enriched track metadata)


@PLAYLISTS_BP.get("/<int:id>")
@login_required
def get_playlist(id):
    try:
        playlist = db_service.get_playlist(playlist_id=id)
    except db_errors.InternalAPINotFoundError:
        return get_error_response(RequestError.NOT_FOUND)

    playlist["tracks"] = _enrich_tracks(playlist.get("tracks", []))
    return playlist, 200


def _enrich_tracks(tracks: list) -> list:
    enriched = []
    for track in tracks:
        track_url = track.get("track_url", "")
        feed_url = track.get("feed_url") or ""
        metadata = {
            "title": None,
            "audio": track_url,
            "artist": None,
            "description": None,
            "image": None,
            "value": None,
        }
        if feed_url:
            try:
                feed = LinkFunctions.get_feed_by_url(feed_url)
                episode = next(
                    (
                        item
                        for item in feed.items
                        if item.get("enclosure_url") == track_url
                    ),
                    None,
                )
                if episode:
                    metadata["title"] = episode.get("title")
                    metadata["artist"] = episode.get("artist") or feed.artist
                    metadata["description"] = episode.get("description")
                    metadata["image"] = episode.get("image") or feed.art_url or None
                else:
                    metadata["title"] = feed.title
                    metadata["artist"] = feed.artist
                    metadata["image"] = feed.art_url or None
                if feed.value_items and feed.value_items[0]:
                    metadata["value"] = feed.value_items[0]
            except ExternalAPIError:
                pass
            except Exception:
                pass
        enriched.append({**track, **metadata})
    return enriched


# Add track to playlist


@PLAYLISTS_BP.post("/<int:id>/tracks/add")
@login_required
def add_track(id):
    user_id = int(get_current_user_id())
    payload = request.get_json(silent=True) or {}

    try:
        request_data = track_reqs.AddTrackToPlaylistRequest(
            exclude=("created_by_user_id",)
        ).load(payload)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    try:
        result = db_service.add_track_to_playlist(
            playlist_id=id,
            user_id=user_id,
            track_url=request_data["track_url"],
            feed_url=request_data.get("feed_url"),
        )
        return result, 201
    except db_errors.InternalAPINotFoundError:
        return get_error_response(RequestError.NOT_FOUND)
    except db_errors.InternalAPIUniquenessError:
        return get_error_response(RequestError.VALUE_NOT_UNIQUE)


# Remove track from playlist


@PLAYLISTS_BP.delete("/<int:id>/tracks/remove")
@login_required
def remove_track(id):
    user_id = int(get_current_user_id())
    payload = request.get_json(silent=True) or {}

    try:
        request_data = track_reqs.RemoveTrackFromPlaylistRequest(
            exclude=("created_by_user_id",)
        ).load(payload)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    try:
        result = db_service.remove_track_from_playlist(
            playlist_id=id,
            user_id=user_id,
            track_url=request_data["track_url"],
        )
        return result, 200
    except db_errors.InternalAPINotFoundError:
        return get_error_response(RequestError.NOT_FOUND)


# Reorder track in playlist


@PLAYLISTS_BP.patch("/<int:id>/tracks/reorder")
@login_required
def reorder_track(id):
    user_id = int(get_current_user_id())
    payload = request.get_json(silent=True) or {}

    try:
        request_data = track_reqs.ReorderTrackRequest(
            exclude=("created_by_user_id",)
        ).load(payload)
    except ValidationError:
        return get_error_response(RequestError.INVALID_ARGUMENT)

    try:
        result = db_service.reorder_playlist_track(
            playlist_id=id,
            user_id=user_id,
            track_url=request_data["track_url"],
            new_position=request_data["new_position"],
        )
        return result, 200
    except db_errors.InternalAPINotFoundError:
        return get_error_response(RequestError.NOT_FOUND)
