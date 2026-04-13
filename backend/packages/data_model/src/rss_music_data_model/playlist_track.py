from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from rss_music_data_model.base import Base


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id: Mapped[int] = mapped_column(primary_key=True)

    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id"))

    track_url: Mapped[str] = mapped_column(String, nullable=False)

    feed_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    position: Mapped[int] = mapped_column(nullable=False)

    added_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("playlist_id", "track_url", name="uix_playlist_id_track_url"),
    )
