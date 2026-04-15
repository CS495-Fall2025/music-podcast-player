"""merge email and playlist migrations

Revision ID: 23193244de59
Revises: 17c71878c2c0, bcb70cd775f3
Create Date: 2026-03-26 11:45:00.728111

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "23193244de59"
down_revision: Union[str, Sequence[str], None] = ("17c71878c2c0", "bcb70cd775f3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
