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
    from rss_music_db_service.logging_config import get_logger, log_request

    logger = get_logger(__name__)
    with make_session() as session:
        user = session.query(User).filter(User.email == email).first()

        log_request(
            logger,
            "info",
            "verify_email_attempt",
            f"Attempting email verification for {email} with code {code}",
            route="/users/verify-email",
            status_code=200,
            email_verified_before=str(user.email_verified) if user else None,
        )

        if user is None:
            log_request(
                logger,
                "warn",
                "verify_email_fail",
                f"No user found for {email}",
                route="/users/verify-email",
                status_code=404,
            )
            return False

        if user.email_verified:
            log_request(
                logger,
                "info",
                "verify_email_already_verified",
                f"User {email} already verified.",
                route="/users/verify-email",
                status_code=200,
            )
            return True

        if user.email_verification_code != code:
            log_request(
                logger,
                "warn",
                "verify_email_fail",
                f"Verification code mismatch for {email}",
                route="/users/verify-email",
                status_code=400,
            )
            return False

        expires_at = user.email_verification_code_expires_at
        if expires_at is None or expires_at.replace(tzinfo=timezone.utc) < datetime.now(
            timezone.utc
        ):
            log_request(
                logger,
                "warn",
                "verify_email_fail",
                f"Verification code expired for {email}",
                route="/users/verify-email",
                status_code=400,
            )
            return False

        user.email_verified = True
        user.email_verification_code = None
        user.email_verification_code_expires_at = None
        session.commit()

        log_request(
            logger,
            "info",
            "verify_email_success",
            f"Email verified for {email}",
            route="/users/verify-email",
            status_code=200,
            email_verified_after=str(user.email_verified),
        )

        return True
