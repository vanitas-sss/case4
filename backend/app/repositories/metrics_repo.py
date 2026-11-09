from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.metric import Metric


def _utc_naive(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def add_metric(
    db: Session,
    host_id: int,
    timestamp: datetime,
    cpu_percent: Optional[float] = None,
    memory_percent: Optional[float] = None,
    disk_percent: Optional[float] = None,
    net_rx_bytes: Optional[int] = None,
    net_tx_bytes: Optional[int] = None,
) -> Metric:
    metric = Metric(
        host_id=host_id,
        timestamp=_utc_naive(timestamp),
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        disk_percent=disk_percent,
        net_rx_bytes=net_rx_bytes,
        net_tx_bytes=net_tx_bytes,
    )
    db.add(metric)
    db.flush()
    return metric


def list_metrics(
    db: Session,
    host_id: int,
    since: Optional[datetime] = None,
    limit: int = 500,
) -> list[Metric]:
    query = db.query(Metric).filter(Metric.host_id == host_id)
    if since is not None:
        query = query.filter(Metric.timestamp >= _utc_naive(since))
    return query.order_by(Metric.timestamp.desc()).limit(limit).all()


def get_latest_metric(db: Session, host_id: int) -> Optional[Metric]:
    return (
        db.query(Metric)
        .filter(Metric.host_id == host_id)
        .order_by(Metric.timestamp.desc(), Metric.id.desc())
        .first()
    )
