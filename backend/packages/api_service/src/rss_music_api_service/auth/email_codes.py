from datetime import datetime, timedelta, timezone
from flask import current_app
import secrets

CODE_WHEN_DISABLED = "000000"


def generate_code() -> str:
    if current_app.config.get("DISABLE_EMAIL_VERIFY", False):
        return CODE_WHEN_DISABLED
    return f"{secrets.randbelow(1_000_000):06d}"


def generate_expiration(minutes: int = 15) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)
