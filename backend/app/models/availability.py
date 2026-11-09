from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class AvailabilityCheck(Base):
    __tablename__ = "availability_checks"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True)
    checked_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    is_online = Column(Boolean, nullable=False)

    host = relationship("Host", back_populates="availability_checks")
