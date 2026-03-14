from datetime import datetime, timezone

from rss_music_data_model import User, make_session


def set_email_verification_code(email: str, code: str, expires_at: datetime) -> bool:
    with make_session() as session:
        user = session.query(User).filter(User.email == email).first()

        if user is None:
            return False

        user.email_verification_code = code
        user.email_verification_code_expires_at = expires_at
        session.commit()

        return True


def verify_email(email: str, code: str) -> bool:
    with make_session() as session:
        user = session.query(User).filter(User.email == email).first()

        if user is None:
            return False

        if user.email_verified:
            return True

        if user.email_verification_code != code:
            return False

        expires_at = user.email_verification_code_expires_at
        if expires_at is None or expires_at.replace(tzinfo=timezone.utc) < datetime.now(
            timezone.utc
        ):
            return False

        user.email_verified = True
        user.email_verification_code = None
        user.email_verification_code_expires_at = None
        session.commit()

        return True
