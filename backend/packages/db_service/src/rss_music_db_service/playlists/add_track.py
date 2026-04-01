from sqlalchemy.exc import IntegrityError

from rss_music_data_model import Playlist, PlaylistTrack, make_session
from rss_music_db_service.errors import PlaylistNotFoundError, TrackAlreadyExistsError
from rss_music_db_service.logging_config import log_request, get_logger

logger = get_logger(__name__)


def add_track_to_playlist(
    playlist_id: int, user_id: int, track_url: str
) -> PlaylistTrack:
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

        next_position = (
            session.query(PlaylistTrack)
            .filter_by(playlist_id=playlist_id)
            .count()
        ) + 1

        track = PlaylistTrack(
            playlist_id=playlist_id,
            track_url=track_url,
            position=next_position,
        )

        try:
            session.add(track)
            playlist.track_count += 1
            session.commit()
            session.refresh(track)

            result = {
                "id": track.id,
                "playlist_id": track.playlist_id,
                "track_url": track.track_url,
                "position": track.position,
                "added_at": track.added_at,
            }

            log_request(
                logger,
                "info",
                "db_change",
                "Track added to playlist",
                operation="INSERT",
                table="playlist_tracks",
                playlist_id=playlist_id,
            )

            return result

        except IntegrityError:
            session.rollback()
            raise TrackAlreadyExistsError(
                f"Track URL already exists in playlist {playlist_id}"
            )
