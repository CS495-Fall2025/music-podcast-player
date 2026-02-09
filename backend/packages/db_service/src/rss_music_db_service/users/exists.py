from rss_music_data_model import User, make_session


def user_exists_by_username(username: str) -> bool:
    with make_session() as session:
        user = session.query(User).filter(User.username == username).first()

        if user:
            return True

    return False


def user_exists_by_email(email: str) -> bool:
    with make_session() as session:
        user = session.query(User).filter(User.email == email).first()

        if user:
            return True

    return False


def user_exists_by_int(id: int) -> bool:
    with make_session() as session:
        user = session.query(User).filter(User.id == id).first()

        if user:
            return True

    return False
