from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.time import utc_now_naive
from app.db.base import Base


class Metric(Base):
    __tablename__ = "metrics"

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
