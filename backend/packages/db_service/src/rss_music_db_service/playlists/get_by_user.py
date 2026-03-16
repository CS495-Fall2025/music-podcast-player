from backend.packages.db_service.src.rss_music_db_service.errors import UserNotFoundError
from rss_music_data_model import Playlist, User, make_session


def get_playlists_by_user(user_id: int) -> list[Playlist]:
    with make_session() as session:
        user = session.query(User).filter_by(id=user_id).first()

        if not user:
            raise UserNotFoundError(f"User with ID {user_id} does not exist.")

        return session.query(Playlist).filter_by(created_by_user_id=user_id).all()
