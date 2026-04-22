"""Helper to get current user ID and admin status"""

from flask import request, current_app
from rss_music_api_service.auth import login


def _decode_token(check_existence: bool = True) -> dict | None:
    """Decode access token from cookie, returning payload or None."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        secret_key = current_app.config.get("SECRET_KEY")
        return login.verify_jwt(
            token,
            secret_key,
            expected_type=login.TokenType.ACCESS,
            check_existence=check_existence,
        )
    except (login.InvalidTokenError, login.UserNotFoundError):
        return None


# verify_existence will check the DB service to confirm the user exists. If enabled,
# this may return an exception should the DB service have an issue.
def get_current_user_id(check_existence: bool = True) -> str | None:
    """get user ID from JWT token if present."""
    payload = _decode_token(check_existence=check_existence)
    if payload is None:
        return None
    return str(payload.get("sub"))


def get_current_user_is_admin(check_existence: bool = False) -> bool:
    """Return True if the current user's JWT contains is_admin=True."""
    payload = _decode_token(check_existence=check_existence)
    if payload is None:
        return False
    return payload.get("is_admin", False) is True
