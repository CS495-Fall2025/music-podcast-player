"""Helper to get current user ID"""

from flask import request, current_app
from rss_music_api_service.auth import login


def get_current_user_id() -> str | None:
    """get user ID from JWT token if present."""
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        secret_key = current_app.config.get("SECRET_KEY")
        payload = login.verify_jwt(
            token, secret_key, expected_type=login.TokenType.ACCESS
        )
        return str(payload.get("sub"))
    except (login.InvalidTokenError, login.UserNotFoundError, Exception):
        return None
