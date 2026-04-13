from rss_music_data_model import Playlist, User, make_session
from rss_music_db_service.logging_config import get_logger, log_request

logger = get_logger(__name__)


def delete_user(user_id: int) -> bool:
    with make_session() as session:
        user = session.query(User).filter_by(id=user_id).first()

        if not user:
            return False

        playlists = session.query(Playlist).filter_by(created_by_user_id=user_id).all()

        for playlist in playlists:
            session.delete(playlist)

        session.delete(user)
        session.commit()

        log_request(
            logger,
            "info",
            "db_change",
            "User deleted from database",
            operation="DELETE",
            table="users",
            user_id=user_id,
        )

        return True
