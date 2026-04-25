from sqlalchemy.orm import Session

from rss_music_data_model import User

from rss_music_set_admin.errors import UserNotFoundError


def set_admin(
    session: Session, admin: bool, email: str | None = None, username: str | None = None
) -> None:
    if email is not None:
        user = _get_user_by_email(session, email)
    elif username is not None:
        user = _get_user_by_username(session, username)
    else:
        raise ValueError("A username or email for the user needs to be specified")

    user.is_admin = admin
    session.commit()


def _get_user_by_email(session: Session, email: str) -> User:
    user = session.query(User).filter_by(email=email).first()

    if user is None:
        raise UserNotFoundError(f"Could not find a user with the email {email}")

    return user


def _get_user_by_username(session: Session, username: str) -> User:
    user = session.query(User).filter_by(username=username).first()

    if user is None:
        raise UserNotFoundError(f"Could not find a user with the username {username}")

    return user
