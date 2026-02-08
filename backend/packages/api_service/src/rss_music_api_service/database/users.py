from sqlalchemy import LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from rss_music_api_service.database.base import Base


USERNAME_MAX_LENGTH = 30

# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
EMAIL_MAX_LENGTH = 254

# The salt (16B) + hashed password (32B) should be 48 bytes.
PASSWORD_LENGTH = 48


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(USERNAME_MAX_LENGTH), unique=True)
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary(PASSWORD_LENGTH))
