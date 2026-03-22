"""Helper to get current user ID"""

from flask import request, current_app
from rss_music_api_service.auth import login


# verify_existence will check the DB service to confirm the user exists. If enabled,
# this may return an exception should the DB service have an issue.
def get_current_user_id(check_existence: bool = True) -> str | None:
    """get user ID from JWT token if present."""
    token = request.cookies.get("access_token")
#    if "playlists" in request.url:
#        import pdb; pdb.set_trace()
    if not token:
        return None

    try:
        secret_key = current_app.config.get("SECRET_KEY")
        payload = login.verify_jwt(
            token,
            secret_key,
            expected_type=login.TokenType.ACCESS,
            check_existence=check_existence,
        )
        return str(payload.get("sub"))
    except (login.InvalidTokenError, login.UserNotFoundError):
        return None
