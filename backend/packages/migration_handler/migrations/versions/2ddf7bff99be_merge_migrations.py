"""merge migrations

Revision ID: 2ddf7bff99be
Revises: 251e50b93ffd, 5f5280d4564f
Create Date: 2026-04-13 16:40:31.288721

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '2ddf7bff99be'
down_revision: Union[str, Sequence[str], None] = ('251e50b93ffd', '5f5280d4564f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
