from datetime import datetime, timedelta, timezone
import secrets


def generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def generate_expiration(minutes: int = 15) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)
