"""enforce metric and topology integrity

Revision ID: 5376d67bf582
Revises: 08737956c038
Create Date: 2026-11-09 21:05:42.019877

"""

from collections.abc import Sequence

from alembic import op

revision: str = "5376d67bf582"
down_revision: str | Sequence[str] | None = "08737956c038"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("metrics", schema=None) as batch_op:
        batch_op.create_index(
            "ix_metrics_host_timestamp", ["host_id", "timestamp"], unique=False
        )

    with op.batch_alter_table("network_links", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_network_links_target_node",
            "network_nodes",
            ["host_id", "target_id"],
            ["host_id", "external_id"],
            ondelete="CASCADE",
        )
        batch_op.create_foreign_key(
            "fk_network_links_source_node",
            "network_nodes",
            ["host_id", "source_id"],
            ["host_id", "external_id"],
            ondelete="CASCADE",
        )
        batch_op.create_check_constraint(
            "ck_network_links_load_range",
            "load IS NULL OR (load >= 0 AND load <= 100)",
        )

    with op.batch_alter_table("metrics", schema=None) as batch_op:
        batch_op.create_check_constraint(
            "ck_metrics_cpu_percent_range",
            "cpu_percent IS NULL OR (cpu_percent >= 0 AND cpu_percent <= 100)",
        )
        batch_op.create_check_constraint(
            "ck_metrics_memory_percent_range",
            "memory_percent IS NULL OR (memory_percent >= 0 AND memory_percent <= 100)",
        )
        batch_op.create_check_constraint(
            "ck_metrics_disk_percent_range",
            "disk_percent IS NULL OR (disk_percent >= 0 AND disk_percent <= 100)",
        )
        batch_op.create_check_constraint(
            "ck_metrics_net_rx_non_negative",
            "net_rx_bytes IS NULL OR net_rx_bytes >= 0",
        )
        batch_op.create_check_constraint(
            "ck_metrics_net_tx_non_negative",
            "net_tx_bytes IS NULL OR net_tx_bytes >= 0",
        )


def downgrade() -> None:
    with op.batch_alter_table("metrics", schema=None) as batch_op:
        batch_op.drop_constraint("ck_metrics_cpu_percent_range", type_="check")
        batch_op.drop_constraint("ck_metrics_memory_percent_range", type_="check")
        batch_op.drop_constraint("ck_metrics_disk_percent_range", type_="check")
        batch_op.drop_constraint("ck_metrics_net_rx_non_negative", type_="check")
        batch_op.drop_constraint("ck_metrics_net_tx_non_negative", type_="check")

    with op.batch_alter_table("network_links", schema=None) as batch_op:
        batch_op.drop_constraint("ck_network_links_load_range", type_="check")
        batch_op.drop_constraint("fk_network_links_source_node", type_="foreignkey")
        batch_op.drop_constraint("fk_network_links_target_node", type_="foreignkey")

    with op.batch_alter_table("metrics", schema=None) as batch_op:
        batch_op.drop_index("ix_metrics_host_timestamp")
