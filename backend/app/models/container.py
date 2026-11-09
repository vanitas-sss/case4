from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.time import utc_now_naive
from app.db.base import Base


class Container(Base):
    __tablename__ = "containers"
    __table_args__ = (
        UniqueConstraint("host_id", "docker_id", name="uq_containers_host_docker_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(
        Integer, ForeignKey("hosts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    docker_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    image = Column(String(512), nullable=True)
    status = Column(String(64), nullable=False, default="unknown")
    ip = Column(String(64), nullable=True)
    networks = Column(JSON, nullable=False, default=list)
    last_seen = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now_naive)

    host = relationship("Host", back_populates="containers")
