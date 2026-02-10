import hashlib
from datetime import datetime, timedelta, timezone

import jwt

from rss_music_api_service.database import User, make_session


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


def generate_jwt(
    user: User, secret_key: str, expires_in_hours: int = 1, token_type: str = "access"
) -> str:
    """
    Generate a JWT token for a user.

    Args:
        user: The User object to create token for
        secret_key: The secret key for signing the JWT
        expires_in_hours: How many hours the token should be valid for
        token_type: Either "access" or "refresh"

    Returns:
        The signed JWT token string
    """
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=expires_in_hours)

    payload = {
        "sub": user.id,
        "name": user.username,
        "email": user.email,
        "iat": now,
        "exp": expires_at,
        "type": token_type,
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def generate_tokens(user: User, secret_key: str) -> dict:
    """
    Generate both access and refresh tokens for a user.

    Returns:
        Dictionary with 'access_token' (1 hour) and 'refresh_token' (7 days)
    """
    access_token = generate_jwt(
        user, secret_key, expires_in_hours=1, token_type="access"
    )
    refresh_token = generate_jwt(
        user, secret_key, expires_in_hours=168, token_type="refresh"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def verify_jwt(token: str, secret_key: str, expected_type: str = "access") -> dict:
    """
    Verify a JWT token and check if the user still exists in the database.

    Args:
        token: The JWT token to verify
        secret_key: The secret key used to sign the token
        expected_type: Expected token type ("access" or "refresh")

    Raises:
        InvalidTokenError: If token is invalid, expired, or user doesn't exist
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")

    token_type = payload.get("type", "access")
    if token_type != expected_type:
        raise InvalidTokenError(
            f"Invalid token type: expected {expected_type}, got {token_type}"
        )

    # Verify the user still exists in the database
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError("Invalid token: missing user ID")

    with make_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError("User no longer exists")

    return payload
