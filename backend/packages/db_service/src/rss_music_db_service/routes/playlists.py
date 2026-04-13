from rss_music_db_service_schemas.playlists.requests.delete_playlist import (
    DeletePlaylistRequest,
)
from rss_music_db_service_schemas.playlists.requests.update_playlist import (
    UpdatePlaylistRequest,
)
from rss_music_db_service_schemas.playlists.requests.create_playlist import (
    CreatePlaylistRequest,
)
from rss_music_db_service_schemas.playlists.responses.playlist import PlaylistResponse
from rss_music_db_service_schemas.playlists.responses.update_playlist import (
    UpdatePlaylistResponse,
)
from rss_music_db_service_schemas.playlists.responses.create_playlist import (
    CreatePlaylistResponse,
)
from rss_music_db_service_schemas.playlist_tracks.requests.add_track import (
    AddTrackToPlaylistRequest,
)
from rss_music_db_service_schemas.playlist_tracks.requests.remove_track import (
    RemoveTrackFromPlaylistRequest,
)
from rss_music_db_service_schemas.playlist_tracks.requests.reorder_track import (
    ReorderTrackRequest,
)

from rss_music_db_service.errors import (
    UserNotFoundError,
    PlaylistNotFoundError,
    TrackAlreadyExistsError,
)
from fastapi import status, APIRouter, Request, Response
from fastapi.responses import JSONResponse

from rss_music_db_service.playlists import (
    create,
    update,
    delete,
    get_by_user,
    get_by_username,
    add_track,
    remove_track,
    reorder_track,
    get_by_id,
)
from rss_music_db_service.basic_validation import validate_json
from rss_music_db_service.logging_config import log_request, get_logger

playlists = APIRouter()
logger = get_logger(__name__)


@playlists.post("/create", status_code=status.HTTP_201_CREATED)
async def create_playlist(request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        "Create playlist request",
        route="/playlists/create",
    )

    # Validate incoming JSON against Schema
    result = await validate_json(request, CreatePlaylistRequest())
    if isinstance(result, JSONResponse):
        return result

    kwargs = {"title": result["title"], "user_id": result["created_by_user_id"]}
    if "description" in result and result["description"] is not None:
        kwargs["description"] = result["description"]

    try:
        new_playlist = create.create_and_add_playlist(**kwargs)
        log_request(
            logger,
            "info",
            "response_sent",
            "Playlist created",
            route="/playlists/create",
            status_code=201,
        )

        return CreatePlaylistResponse().dump(new_playlist)
    except UserNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "NotFound", "message": "User not found or doesn't exist"},
        )


@playlists.put("/{id}")
async def update_playlist_route(id: int, request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        f"Update playlist {id}",
        route=f"/playlists/{id}",
    )

    result = await validate_json(request, UpdatePlaylistRequest())
    if isinstance(result, JSONResponse):
        return result

    updated = update.update_playlist(
        playlist_id=id,
        user_id=result["created_by_user_id"],
        title=result.get("title"),
        description=result.get("description"),
    )

    if updated is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": "NotFound",
                "message": "Playlist not found or unauthorized",
            },
        )

    return UpdatePlaylistResponse().dump(updated)


@playlists.delete("/{id}")
async def delete_playlist_route(id: int, request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        f"Delete playlist {id}",
        route=f"/playlists/{id}",
    )

    result = await validate_json(request, DeletePlaylistRequest())
    if isinstance(result, JSONResponse):
        return result

    success = delete.delete_playlist(
        playlist_id=id, user_id=result["created_by_user_id"]
    )

    if not success:
        return JSONResponse(
            status_code=404,
            content={
                "error": "NotFound",
                "message": "Playlist not found or unauthorized",
            },
        )

    return {"message": "Deleted"}


@playlists.get("/user/by-username/{username}")
async def get_playlists_by_username_route(username: str):
    try:
        user, user_playlists = get_by_username.get_playlists_by_username(username)
        if not user.profile_public:
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "message": "This profile is private"},
            )
        response_data = PlaylistResponse(many=True).dump(user_playlists)
        return {"playlists": response_data}
    except UserNotFoundError as err:
        return JSONResponse(
            status_code=404,
            content={"error": "NotFound", "message": str(err)},
        )


@playlists.get("/user/{user_id}")
async def get_user_playlists_route(user_id: int):
    log_request(
        logger,
        "info",
        "request_received",
        f"List playlists for user {user_id}",
        route=f"/playlists/user/{user_id}",
    )

    try:
        user_playlists = get_by_user.get_playlists_by_user(user_id)

        response_data = PlaylistResponse(many=True).dump(user_playlists)

        log_request(
            logger,
            "info",
            "response_sent",
            "Playlists listed",
            route=f"/playlists/user/{user_id}",
            status_code=200,
        )
        return {"playlists": response_data}

    except UserNotFoundError as err:
        return JSONResponse(
            status_code=404,
            content={"error": "NotFound", "message": str(err)},
        )


@playlists.get("/{id}")
async def get_playlist_route(id: int):
    log_request(
        logger,
        "info",
        "request_received",
        f"Get playlist {id}",
        route=f"/playlists/{id}",
    )

    try:
        playlist_data = get_by_id.get_playlist_by_id(id)
        return playlist_data
    except PlaylistNotFoundError as err:
        return JSONResponse(
            status_code=404,
            content={"error": "NotFound", "message": str(err)},
        )


@playlists.post("/{id}/tracks/add", status_code=status.HTTP_201_CREATED)
async def add_track_route(id: int, request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        f"Add track to playlist {id}",
        route=f"/playlists/{id}/tracks/add",
    )

    result = await validate_json(request, AddTrackToPlaylistRequest())
    if isinstance(result, JSONResponse):
        return result

    try:
        track_data = add_track.add_track_to_playlist(
            playlist_id=id,
            user_id=result["created_by_user_id"],
            track_url=result["track_url"],
            feed_url=result.get("feed_url"),
        )
        return track_data
    except PlaylistNotFoundError as err:
        return JSONResponse(
            status_code=404,
            content={"error": "NotFound", "message": str(err)},
        )
    except TrackAlreadyExistsError as err:
        return JSONResponse(
            status_code=409,
            content={
                "error": "NotUnique",
                "message": str(err),
                "details": {"field": "track_url"},
            },
        )


@playlists.delete("/{id}/tracks/remove")
async def remove_track_route(id: int, request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        f"Remove track from playlist {id}",
        route=f"/playlists/{id}/tracks/remove",
    )

    result = await validate_json(request, RemoveTrackFromPlaylistRequest())
    if isinstance(result, JSONResponse):
        return result

    try:
        removed_id = remove_track.remove_track_from_playlist(
            playlist_id=id,
            user_id=result["created_by_user_id"],
            track_url=result["track_url"],
        )
        return {"message": "Track removed", "playlist_track_id": removed_id}
    except PlaylistNotFoundError as err:
        return JSONResponse(
            status_code=404,
            content={"error": "NotFound", "message": str(err)},
        )


@playlists.patch("/{id}/tracks/reorder")
async def reorder_track_route(id: int, request: Request, response: Response):
    log_request(
        logger,
        "info",
        "request_received",
        f"Reorder track in playlist {id}",
        route=f"/playlists/{id}/tracks/reorder",
    )

    result = await validate_json(request, ReorderTrackRequest())
    if isinstance(result, JSONResponse):
        return result

    try:
        track_data = reorder_track.reorder_track(
            playlist_id=id,
            user_id=result["created_by_user_id"],
            track_url=result["track_url"],
            new_position=result["new_position"],
        )
        return track_data
    except PlaylistNotFoundError as err:
        return JSONResponse(
            status_code=404,
            content={"error": "NotFound", "message": str(err)},
        )
