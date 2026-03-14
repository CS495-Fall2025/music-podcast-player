"""Add users table

Revision ID: 254cb91c2ca1
Revises:
Create Date: 2026-01-16 02:09:41.385802

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "254cb91c2ca1"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password", sa.LargeBinary(length=48), nullable=False),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.Column("email_verification_code", sa.String(length=6), nullable=True),
        sa.Column(
            "email_verification_code_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("password_reset_code", sa.String(length=6), nullable=True),
        sa.Column(
            "password_reset_code_expires_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
