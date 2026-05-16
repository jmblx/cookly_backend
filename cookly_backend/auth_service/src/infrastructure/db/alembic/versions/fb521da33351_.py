"""Добавление поля search_name и GIN-индексов для поиска

Revision ID: fb521da33351
Revises: 5596046d3be1
Create Date: 2025-06-02 00:31:14.520167
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "fb521da33351"
down_revision: str | None = "5596046d3be1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "client",
        sa.Column(
            "search_name", sa.String(), nullable=False, server_default=""
        ),
    )
    op.add_column(
        "resource_server",
        sa.Column(
            "search_name", sa.String(), nullable=False, server_default=""
        ),
    )

    op.execute("UPDATE client SET search_name = LOWER(name);")
    op.execute("UPDATE resource_server SET search_name = LOWER(name);")

    op.alter_column("client", "search_name", server_default=None)
    op.alter_column("resource_server", "search_name", server_default=None)

    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    op.execute(
        "CREATE INDEX idx_client_search_name_trgm ON client USING gin (search_name gin_trgm_ops);"
    )
    op.execute(
        "CREATE INDEX idx_resource_server_search_name_trgm ON resource_server USING gin (search_name gin_trgm_ops);"
    )

    op.alter_column(
        "user", "is_admin", existing_type=sa.BOOLEAN(), nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "user", "is_admin", existing_type=sa.BOOLEAN(), nullable=True
    )

    op.execute("DROP INDEX IF EXISTS idx_resource_server_search_name_trgm;")
    op.execute("DROP INDEX IF EXISTS idx_client_search_name_trgm;")

    op.drop_column("resource_server", "search_name")
    op.drop_column("client", "search_name")
