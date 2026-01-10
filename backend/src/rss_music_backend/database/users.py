from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from rss_music_backend.database.base import Base


USERNAME_MAX_LENGTH = 40

# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
EMAIL_MAX_LENGTH = 254

# Using bcrypt, the salted + hashed password should be 60 chars exactly.
PASSWORD_MAX_LENGTH = 60


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(USERNAME_MAX_LENGTH))
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH))
    password: Mapped[str] = mapped_column(String(PASSWORD_MAX_LENGTH))


