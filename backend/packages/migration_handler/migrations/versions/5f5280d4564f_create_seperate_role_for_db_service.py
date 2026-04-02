"""Create seperate role for db service

Revision ID: 5f5280d4564f
Revises: 23193244de59
Create Date: 2026-04-01 21:31:49.021234

"""

from typing import Sequence, Union
import os

from alembic import op
import sqlalchemy as sa

ROLE_NAME = "rssmusicplayerapp"

# revision identifiers, used by Alembic.
revision: str = '5f5280d4564f'
down_revision: Union[str, Sequence[str], None] = '23193244de59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Use to enable password authentication for local development. This variable should be
# unset when deployed to AWS, as IAM will handle authentication there.
role_password = os.getenv("DB_SERVICE_ROLE_PASSWORD")


def upgrade() -> None:
    """Upgrade schema."""
    if role_password is not None:
        op.execute(
            f"CREATE ROLE {ROLE_NAME} WITH LOGIN PASSWORD '{role_password}';"
        )
    else:
        op.execute(f"CREATE ROLE {ROLE_NAME} WITH LOGIN;")

    # Giving the new role access to tables that've already been created.
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public "
        f"TO {ROLE_NAME};"
    )

    # Giving the new role access to tables created in the future.
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {ROLE_NAME};"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f"DROP ROLE IF EXISTS {ROLE_NAME};")
