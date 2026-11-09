from sqlalchemy import Column, Float, ForeignKey, Integer, String, UniqueConstraint

from app.db.base import Base


class NetworkNode(Base):
    __tablename__ = "network_nodes"
    __table_args__ = (
        UniqueConstraint("host_id", "external_id", name="uq_network_nodes_host_external"),
    )

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id = Column(String(255), nullable=False)
    label = Column(String(255), nullable=True)
    type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=True)
    ip = Column(String(64), nullable=True)


class NetworkLink(Base):
    __tablename__ = "network_links"
    __table_args__ = (
        UniqueConstraint(
            "host_id", "source_id", "target_id", "type",
            name="uq_network_links_host_endpoints_type",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(255), nullable=False)
    target_id = Column(String(255), nullable=False)
    type = Column(String(32), nullable=False)
    load = Column(Float, nullable=True)
