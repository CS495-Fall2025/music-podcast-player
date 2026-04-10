"""add metadata columns to playlist_tracks

Revision ID: add_playlist_track_metadata
Revises: 861aef5cce61
Create Date: 2026-04-09

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f3c1b2a7d4e"
down_revision: Union[str, Sequence[str], None] = "394d642fec21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "playlist_tracks",
        sa.Column("title", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "playlist_tracks",
        sa.Column("artist", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "playlist_tracks",
        sa.Column("description", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "playlist_tracks",
        sa.Column("audio", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "playlist_tracks",
        sa.Column("image", sa.String(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("playlist_tracks", "image")
    op.drop_column("playlist_tracks", "audio")
    op.drop_column("playlist_tracks", "description")
    op.drop_column("playlist_tracks", "artist")
    op.drop_column("playlist_tracks", "title")