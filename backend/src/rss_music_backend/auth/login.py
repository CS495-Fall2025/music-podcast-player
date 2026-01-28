import hashlib
from datetime import datetime, timedelta, timezone

import jwt

from rss_music_backend.database import User, make_session


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


def verify_password(stored_salt_and_hash: bytes, provided_password: str) -> bool:
    """
    Verify a password against stored salt + hash.
    """
    salt = stored_salt_and_hash[:16]
    stored_hash = stored_salt_and_hash[16:]
    
    computed_hash = hashlib.scrypt(
        provided_password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=32
    )
    
    return computed_hash == stored_hash


def authenticate_user(username: str, password: str) -> User:
    with make_session() as session:
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            raise InvalidCredentialsError("Invalid credentials")
        
        if not verify_password(user.password, password):
            raise InvalidCredentialsError("Invalid credentials")
        
        return user


def generate_jwt(user: User, secret_key: str, expires_in_hours: int = 7) -> str:
    """
    Generate a JWT token for a user.
    
    Args:
        user: The User object to create token for
        secret_key: The secret key for signing the JWT
        expires_in_hours: How many hours the token should be valid for (default: 7 days)
    
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
    }
    
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def verify_jwt(token: str, secret_key: str) -> dict:
    """
    Verify a JWT token and check if the user still exists in the database.
    
    Raises:
        InvalidTokenError: If token is invalid, expired, or user doesn't exist
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")
    
    # Verify the user still exists in the database
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError("Invalid token: missing user ID")
    
    with make_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise InvalidTokenError("User no longer exists")
    
    return payload