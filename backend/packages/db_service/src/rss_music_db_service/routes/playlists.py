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

from rss_music_db_service.errors import UserNotFoundError
from fastapi import status, APIRouter, Request, Response
from fastapi.responses import JSONResponse

from rss_music_db_service.playlists import create, update, delete, get_by_user
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

    new_playlist = create.create_and_add_playlist(
        title=result["title"],
        user_id=result["created_by_user_id"],
        description=result.get("description"),
    )

    log_request(
        logger,
        "info",
        "response_sent",
        "Playlist created",
        route="/playlists/create",
        status_code=201,
    )

    # Return using Response Schema
    return CreatePlaylistResponse().dump(new_playlist)


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
            status_code=404, content={"message": "Playlist not found or unauthorized"}
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
            status_code=404, content={"message": "Playlist not found or unauthorized"}
        )

    return {"message": "Deleted"}


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
    except UserNotFoundError as e:
        return JSONResponse(status_code=404, content={"message": str(e)})

        # Format response
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
