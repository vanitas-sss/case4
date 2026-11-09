from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.time import utc_now_naive
from app.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(
        Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    container_id = Column(
        Integer,
        ForeignKey("containers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    timestamp = Column(
        DateTime(timezone=True), nullable=False, default=utc_now_naive, index=True
    )
    type = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=True)

    host = relationship("Host", back_populates="events")
    container = relationship("Container")
