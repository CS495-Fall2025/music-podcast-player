from rss_music_data_model import Playlist, make_session
from rss_music_db_service.logging_config import log_request, get_logger

logger = get_logger(__name__)


def delete_playlist(playlist_id: int, user_id: int) -> bool:
    with make_session() as session:
        playlist = (
            session.query(Playlist)
            .filter_by(id=playlist_id, created_by_user_id=user_id)
            .first()
        )

        if not playlist:
            return False

        session.delete(playlist)
        session.commit()

        log_request(
            logger,
            "info",
            "db_change",
            "Playlist deleted",
            operation="DELETE",
            table="playlists",
            playlist_id=playlist_id,
        )
        return True
