from rss_music_data_model import Playlist, PlaylistTrack, make_session
from rss_music_db_service.errors import PlaylistNotFoundError
from rss_music_db_service.logging_config import log_request, get_logger

logger = get_logger(__name__)


def remove_track_from_playlist(playlist_id: int, user_id: int, track_url: str) -> int:
    """Remove a track from a playlist. Returns the removed track's id."""
    with make_session() as session:
        playlist = (
            session.query(Playlist)
            .filter_by(id=playlist_id, created_by_user_id=user_id)
            .first()
        )

        if not playlist:
            raise PlaylistNotFoundError(
                f"Playlist {playlist_id} not found or unauthorized"
            )

        track = (
            session.query(PlaylistTrack)
            .filter_by(playlist_id=playlist_id, track_url=track_url)
            .first()
        )

        if not track:
            raise PlaylistNotFoundError(f"Track not found in playlist {playlist_id}")

        removed_id = track.id
        removed_position = track.position

        session.delete(track)

        # Shift positions of tracks that came after the removed one
        session.query(PlaylistTrack).filter(
            PlaylistTrack.playlist_id == playlist_id,
            PlaylistTrack.position > removed_position,
        ).update({"position": PlaylistTrack.position - 1})

        if playlist.track_count > 0:
            playlist.track_count -= 1

        session.commit()

        log_request(
            logger,
            "info",
            "db_change",
            "Track removed from playlist",
            operation="DELETE",
            table="playlist_tracks",
            playlist_id=playlist_id,
        )

        return removed_id
