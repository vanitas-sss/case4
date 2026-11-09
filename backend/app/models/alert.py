from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.time import utc_now_naive
from app.db.base import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, unique=True)
    metric = Column(String(80), nullable=False)
    operator = Column(String(8), nullable=False, default=">")
    threshold = Column(Float, nullable=False)
    duration_seconds = Column(Integer, nullable=False, default=0)
    severity = Column(String(32), nullable=False, default="warning")
    enabled = Column(Boolean, nullable=False, default=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(
        Integer, ForeignKey("hosts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    rule = Column(String(120), nullable=False, index=True)
    target = Column(String(255), nullable=False)
    severity = Column(String(32), nullable=False, default="warning")
    status = Column(String(32), nullable=False, default="active", index=True)
    message = Column(Text, nullable=True)
    started_at = Column(
        DateTime(timezone=True), nullable=False, default=utc_now_naive, index=True
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    host = relationship("Host", back_populates="alerts")
