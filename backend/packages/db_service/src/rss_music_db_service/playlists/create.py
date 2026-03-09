from sqlalchemy.exc import IntegrityError
from rss_music_data_model import Playlist, make_session
from rss_music_db_service.logging_config import log_request, get_logger

logger = get_logger(__name__)


def create_and_add_playlist(
    title: str, user_id: int, description: str = None
) -> Playlist:
    playlist = Playlist(
        title=title, created_by_user_id=user_id, description=description
    )

    with make_session() as session:
        try:
            session.add(playlist)
            session.commit()
            # Refresh to get the ID assigned by the DB
            session.refresh(playlist)

            log_request(
                logger,
                "info",
                "db_change",
                "Playlist created",
                operation="INSERT",
                table="playlists",
                title=title,
            )
            return playlist
        except IntegrityError as error:
            session.rollback()
            raise error
