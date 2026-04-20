from rss_music_data_model import Playlist, PlaylistTrack, make_session
from rss_music_db_service.errors import PlaylistNotFoundError
from rss_music_db_service.logging_config import log_request, get_logger

logger = get_logger(__name__)


def reorder_track(
    playlist_id: int, user_id: int, track_url: str, new_position: int
) -> dict:
    """Move a track to new_position, shifting other tracks to fill the gap."""
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

        track_count = (
            session.query(PlaylistTrack).filter_by(playlist_id=playlist_id).count()
        )
        new_position = max(1, min(new_position, track_count))

        old_position = track.position
        if old_position == new_position:
            return {
                "id": track.id,
                "playlist_id": track.playlist_id,
                "track_url": track.track_url,
                "position": track.position,
                "added_at": track.added_at,
            }

        if old_position < new_position:
            # Moving down: shift tracks between old+1 and new_position up by 1
            session.query(PlaylistTrack).filter(
                PlaylistTrack.playlist_id == playlist_id,
                PlaylistTrack.position > old_position,
                PlaylistTrack.position <= new_position,
            ).update({"position": PlaylistTrack.position - 1})
        else:
            # Moving up: shift tracks between new_position and old-1 down by 1
            session.query(PlaylistTrack).filter(
                PlaylistTrack.playlist_id == playlist_id,
                PlaylistTrack.position >= new_position,
                PlaylistTrack.position < old_position,
            ).update({"position": PlaylistTrack.position + 1})

        track.position = new_position
        session.commit()
        session.refresh(track)

        log_request(
            logger,
            "info",
            "db_change",
            "Track reordered",
            operation="UPDATE",
            table="playlist_tracks",
            playlist_id=playlist_id,
        )

        return {
            "id": track.id,
            "playlist_id": track.playlist_id,
            "track_url": track.track_url,
            "position": track.position,
            "added_at": track.added_at,
        }
