"""add email verification columns

Revision ID: 17c71878c2c0
Revises: 254cb91c2ca1
Create Date: 2026-03-19 12:13:21.779984

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "17c71878c2c0"
down_revision: Union[str, Sequence[str], None] = "254cb91c2ca1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    users = sa.table("users", sa.column("email_verified", sa.Boolean()))
    op.add_column(
        "users",
        sa.Column(
            "email_verified", sa.Boolean(), nullable=True, server_default=sa.false()
        ),
    )
    op.add_column(
        "users",
        sa.Column("email_verification_code", sa.String(length=6), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "email_verification_code_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "users", sa.Column("password_reset_code", sa.String(length=6), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column(
            "password_reset_code_expires_at", sa.DateTime(timezone=True), nullable=True
        ),
    )
    op.execute(
        users.update()
        .where(users.c.email_verified.is_(None))
        .values(email_verified=sa.false())
    )
    op.alter_column(
        "users",
        "email_verified",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "password_reset_code_expires_at")
    op.drop_column("users", "password_reset_code")
    op.drop_column("users", "email_verification_code_expires_at")
    op.drop_column("users", "email_verification_code")
    op.drop_column("users", "email_verified")
