from sqlalchemy import (
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
)

from app.db.base import Base


class NetworkNode(Base):
    __tablename__ = "network_nodes"
    __table_args__ = (
        UniqueConstraint(
            "host_id", "external_id", name="uq_network_nodes_host_external"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(
        Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    external_id = Column(String(255), nullable=False)
    label = Column(String(255), nullable=True)
    type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=True)
    ip = Column(String(64), nullable=True)


class NetworkLink(Base):
    __tablename__ = "network_links"
    __table_args__ = (
        UniqueConstraint(
            "host_id",
            "source_id",
            "target_id",
            "type",
            name="uq_network_links_host_endpoints_type",
        ),
        ForeignKeyConstraint(
            ["host_id", "source_id"],
            ["network_nodes.host_id", "network_nodes.external_id"],
            ondelete="CASCADE",
            name="fk_network_links_source_node",
        ),
        ForeignKeyConstraint(
            ["host_id", "target_id"],
            ["network_nodes.host_id", "network_nodes.external_id"],
            ondelete="CASCADE",
            name="fk_network_links_target_node",
        ),
        CheckConstraint(
            "load IS NULL OR (load >= 0 AND load <= 100)",
            name="ck_network_links_load_range",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(
        Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id = Column(String(255), nullable=False)
    target_id = Column(String(255), nullable=False)
    type = Column(String(32), nullable=False)
    load = Column(Float, nullable=True)
