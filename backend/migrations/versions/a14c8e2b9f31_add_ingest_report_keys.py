"""Add ingest report idempotency keys.

Revision ID: a14c8e2b9f31
Revises: 5376d67bf582
Create Date: 2026-11-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a14c8e2b9f31"
down_revision: str | Sequence[str] | None = "5376d67bf582"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ingest_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("host_name", sa.String(length=255), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_id",
            "host_name",
            "timestamp",
            name="uq_ingest_reports_source_host_timestamp",
        ),
    )
    op.create_index("ix_ingest_reports_id", "ingest_reports", ["id"], unique=False)
    op.create_index(
        "ix_ingest_reports_timestamp",
        "ingest_reports",
        ["timestamp"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ingest_reports_timestamp", table_name="ingest_reports")
    op.drop_index("ix_ingest_reports_id", table_name="ingest_reports")
    op.drop_table("ingest_reports")
