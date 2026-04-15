from rss_music_data_model import User, make_session
from rss_music_db_service.logging_config import log_request, get_logger

logger = get_logger(__name__)


def get_profile_public(user_id: int) -> bool:
    with make_session() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return True
        return user.profile_public


def set_profile_public(user_id: int, profile_public: bool) -> bool:
    with make_session() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return False
        user.profile_public = profile_public
        session.commit()
        log_request(
            logger,
            "info",
            "db_change",
            "User profile visibility updated",
            operation="UPDATE",
            table="users",
            user_id=user_id,
            profile_public=profile_public,
        )
        return True
