from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
)
from sqlalchemy.orm import relationship

from app.core.time import utc_now_naive
from app.db.base import Base


class Metric(Base):
    __tablename__ = "metrics"
    __table_args__ = (
        CheckConstraint(
            "cpu_percent IS NULL OR (cpu_percent >= 0 AND cpu_percent <= 100)",
            name="ck_metrics_cpu_percent_range",
        ),
        CheckConstraint(
            "memory_percent IS NULL OR (memory_percent >= 0 AND memory_percent <= 100)",
            name="ck_metrics_memory_percent_range",
        ),
        CheckConstraint(
            "disk_percent IS NULL OR (disk_percent >= 0 AND disk_percent <= 100)",
            name="ck_metrics_disk_percent_range",
        ),
        CheckConstraint(
            "net_rx_bytes IS NULL OR net_rx_bytes >= 0",
            name="ck_metrics_net_rx_non_negative",
        ),
        CheckConstraint(
            "net_tx_bytes IS NULL OR net_tx_bytes >= 0",
            name="ck_metrics_net_tx_non_negative",
        ),
        Index("ix_metrics_host_timestamp", "host_id", "timestamp"),
    )

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(
        Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp = Column(
        DateTime(timezone=True), nullable=False, default=utc_now_naive, index=True
    )
    cpu_percent = Column(Float, nullable=True)
    memory_percent = Column(Float, nullable=True)
    disk_percent = Column(Float, nullable=True)
    net_rx_bytes = Column(BigInteger, nullable=True)
    net_tx_bytes = Column(BigInteger, nullable=True)

    host = relationship("Host", back_populates="metrics")
