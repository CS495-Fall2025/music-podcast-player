from sqlalchemy.orm import selectinload

from rss_music_db_service.errors import UserNotFoundError
from rss_music_data_model import Playlist, User, make_session


def get_playlists_by_username(username: str) -> tuple:
    with make_session() as session:
        user = session.query(User).filter_by(username=username).first()

        if not user:
            raise UserNotFoundError(f"User with username {username} does not exist")

        playlists = (
            session.query(Playlist)
            .options(selectinload(Playlist.tracks))
            .filter_by(created_by_user_id=user.id)
            .all()
        )

        # Capture profile_public before session closes
        profile_public = user.profile_public

        # Return a plain object so profile_public is accessible after session closes
        class UserInfo:
            pass

        user_info = UserInfo()
        user_info.profile_public = profile_public

        return user_info, playlists
