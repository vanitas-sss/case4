from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c07d4c202611"
down_revision: str | Sequence[str] | None = "a14c8e2b9f31"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("containers", sa.Column("stopped_since", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("containers", "stopped_since")
