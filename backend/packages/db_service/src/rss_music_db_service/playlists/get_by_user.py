from rss_music_data_model import Playlist, make_session


def get_playlists_by_user(user_id: int) -> list[Playlist]:
    with make_session() as session:
        return session.query(Playlist).filter_by(created_by_user_id=user_id).all()
