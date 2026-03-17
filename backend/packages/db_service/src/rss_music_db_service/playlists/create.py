from rss_music_data_model.users import User
from rss_music_db_service.errors import UserNotFoundError
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
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(
                f"Failed to create playlist: User ID {user_id} does not exist.")
            raise UserNotFoundError(f"User ID {user_id} does not exist.")

        try:
            session.add(playlist)
            session.commit()
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

            logger.error(f"Failed to create playlist: {error}")
            raise UserNotFoundError(
                f"User ID {user_id} does not exist.") from error
