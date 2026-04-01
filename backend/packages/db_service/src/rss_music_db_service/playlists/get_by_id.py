from rss_music_data_model import Playlist, make_session
from rss_music_db_service.errors import PlaylistNotFoundError
from rss_music_db_service.logging_config import log_request, get_logger

logger = get_logger(__name__)


def get_playlist_by_id(playlist_id: int) -> dict:
    """Return playlist data with track URLs. Builds a plain dict within the
    session to avoid detached-instance errors on the relationship."""
    with make_session() as session:
        playlist = session.query(Playlist).filter_by(id=playlist_id).first()

        if not playlist:
            raise PlaylistNotFoundError(f"Playlist {playlist_id} not found")

        tracks = [
            {
                "id": t.id,
                "playlist_id": t.playlist_id,
                "track_url": t.track_url,
                "position": t.position,
                "added_at": t.added_at,
            }
            for t in playlist.tracks
        ]

        result = {
            "id": playlist.id,
            "title": playlist.title,
            "description": playlist.description,
            "track_count": playlist.track_count,
            "created_by_user_id": playlist.created_by_user_id,
            "created_at": playlist.created_at,
            "tracks": tracks,
        }

        log_request(
            logger,
            "info",
            "db_read",
            "Playlist fetched by ID",
            operation="SELECT",
            table="playlists",
            playlist_id=playlist_id,
        )

        return result
