from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rss_music_data_model.base import Base


if TYPE_CHECKING:
    from rss_music_data_model.playlist import Playlist


USERNAME_MAX_LENGTH = 30

# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
EMAIL_MAX_LENGTH = 254

# The salt (16B) + hashed password (32B) should be 48 bytes.
PASSWORD_LENGTH = 48
CODE_LENGTH = 6


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(USERNAME_MAX_LENGTH), unique=True)
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary(PASSWORD_LENGTH))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    profile_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    playlists: Mapped[list["Playlist"]] = relationship(
        "Playlist", cascade="all, delete-orphan", passive_deletes=True
    )
    email_verification_code: Mapped[str | None] = mapped_column(
        String(CODE_LENGTH), nullable=True
    )
    email_verification_code_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    password_reset_code: Mapped[str | None] = mapped_column(
        String(CODE_LENGTH), nullable=True
    )
    password_reset_code_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
