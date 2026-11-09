from sqlalchemy import Column, DateTime, Index, Integer, String, UniqueConstraint

from app.db.base import Base


class IngestReport(Base):
    __tablename__ = "ingest_reports"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "host_name",
            "timestamp",
            name="uq_ingest_reports_source_host_timestamp",
        ),
        Index("ix_ingest_reports_timestamp", "timestamp"),
    )

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(255), nullable=False)
    host_name = Column(String(255), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
