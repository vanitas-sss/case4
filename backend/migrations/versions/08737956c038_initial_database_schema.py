"""initial database schema

Revision ID: 08737956c038
Revises:
Create Date: 2026-11-09 21:01:37.624778

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "08737956c038"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("metric", sa.String(length=80), nullable=False),
        sa.Column("operator", sa.String(length=8), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    with op.batch_alter_table("alert_rules", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_alert_rules_id"), ["id"], unique=False)

    op.create_table(
        "hosts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "name", name="uq_hosts_source_name"),
    )
    with op.batch_alter_table("hosts", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_hosts_id"), ["id"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_hosts_last_seen"), ["last_seen"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_hosts_name"), ["name"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_hosts_source_id"), ["source_id"], unique=False
        )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=True),
        sa.Column("rule", sa.String(length=120), nullable=False),
        sa.Column("target", sa.String(length=255), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["host_id"], ["hosts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("alerts", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_alerts_host_id"), ["host_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_alerts_id"), ["id"], unique=False)
        batch_op.create_index(batch_op.f("ix_alerts_rule"), ["rule"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_alerts_started_at"), ["started_at"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_alerts_status"), ["status"], unique=False)

    op.create_table(
        "availability_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_online", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["hosts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("availability_checks", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_availability_checks_checked_at"),
            ["checked_at"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_availability_checks_host_id"), ["host_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_availability_checks_id"), ["id"], unique=False
        )

    op.create_table(
        "containers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("docker_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("image", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("networks", sa.JSON(), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["hosts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "host_id", "docker_id", name="uq_containers_host_docker_id"
        ),
    )
    with op.batch_alter_table("containers", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_containers_docker_id"), ["docker_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_containers_host_id"), ["host_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_containers_id"), ["id"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_containers_last_seen"), ["last_seen"], unique=False
        )

    op.create_table(
        "metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cpu_percent", sa.Float(), nullable=True),
        sa.Column("memory_percent", sa.Float(), nullable=True),
        sa.Column("disk_percent", sa.Float(), nullable=True),
        sa.Column("net_rx_bytes", sa.BigInteger(), nullable=True),
        sa.Column("net_tx_bytes", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["host_id"], ["hosts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("metrics", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_metrics_host_id"), ["host_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_metrics_id"), ["id"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_metrics_timestamp"), ["timestamp"], unique=False
        )

    op.create_table(
        "network_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("target_id", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("load", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["host_id"], ["hosts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "host_id",
            "source_id",
            "target_id",
            "type",
            name="uq_network_links_host_endpoints_type",
        ),
    )
    with op.batch_alter_table("network_links", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_network_links_host_id"), ["host_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_network_links_id"), ["id"], unique=False)

    op.create_table(
        "network_nodes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=True),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["host_id"], ["hosts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "host_id", "external_id", name="uq_network_nodes_host_external"
        ),
    )
    with op.batch_alter_table("network_nodes", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_network_nodes_host_id"), ["host_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_network_nodes_id"), ["id"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("container_id", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["container_id"], ["containers.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["host_id"], ["hosts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("events", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_events_container_id"), ["container_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_events_host_id"), ["host_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_events_id"), ["id"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_events_timestamp"), ["timestamp"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_events_type"), ["type"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("events", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_events_type"))
        batch_op.drop_index(batch_op.f("ix_events_timestamp"))
        batch_op.drop_index(batch_op.f("ix_events_id"))
        batch_op.drop_index(batch_op.f("ix_events_host_id"))
        batch_op.drop_index(batch_op.f("ix_events_container_id"))

    op.drop_table("events")
    with op.batch_alter_table("network_nodes", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_network_nodes_id"))
        batch_op.drop_index(batch_op.f("ix_network_nodes_host_id"))

    op.drop_table("network_nodes")
    with op.batch_alter_table("network_links", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_network_links_id"))
        batch_op.drop_index(batch_op.f("ix_network_links_host_id"))

    op.drop_table("network_links")
    with op.batch_alter_table("metrics", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_metrics_timestamp"))
        batch_op.drop_index(batch_op.f("ix_metrics_id"))
        batch_op.drop_index(batch_op.f("ix_metrics_host_id"))

    op.drop_table("metrics")
    with op.batch_alter_table("containers", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_containers_last_seen"))
        batch_op.drop_index(batch_op.f("ix_containers_id"))
        batch_op.drop_index(batch_op.f("ix_containers_host_id"))
        batch_op.drop_index(batch_op.f("ix_containers_docker_id"))

    op.drop_table("containers")
    with op.batch_alter_table("availability_checks", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_availability_checks_id"))
        batch_op.drop_index(batch_op.f("ix_availability_checks_host_id"))
        batch_op.drop_index(batch_op.f("ix_availability_checks_checked_at"))

    op.drop_table("availability_checks")
    with op.batch_alter_table("alerts", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_alerts_status"))
        batch_op.drop_index(batch_op.f("ix_alerts_started_at"))
        batch_op.drop_index(batch_op.f("ix_alerts_rule"))
        batch_op.drop_index(batch_op.f("ix_alerts_id"))
        batch_op.drop_index(batch_op.f("ix_alerts_host_id"))

    op.drop_table("alerts")
    with op.batch_alter_table("hosts", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_hosts_source_id"))
        batch_op.drop_index(batch_op.f("ix_hosts_name"))
        batch_op.drop_index(batch_op.f("ix_hosts_last_seen"))
        batch_op.drop_index(batch_op.f("ix_hosts_id"))

    op.drop_table("hosts")
    with op.batch_alter_table("alert_rules", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_alert_rules_id"))

    op.drop_table("alert_rules")
