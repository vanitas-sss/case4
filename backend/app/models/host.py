from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Host(Base):
    __tablename__ = "hosts"
    __table_args__ = (
        UniqueConstraint("source_id", "name", name="uq_hosts_source_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    ip = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="unknown")
    last_seen = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    metrics = relationship("Metric", back_populates="host", cascade="all, delete-orphan")
    containers = relationship("Container", back_populates="host", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="host", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="host")
    availability_checks = relationship("AvailabilityCheck", back_populates="host", cascade="all, delete-orphan")
