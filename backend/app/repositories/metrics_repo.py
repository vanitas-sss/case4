from datetime import datetime

from sqlalchemy.orm import Session

from app.core.time import to_utc_naive
from app.models.metric import Metric


def add_metric(
    db: Session,
    host_id: int,
    timestamp: datetime,
    cpu_percent: float | None = None,
    memory_percent: float | None = None,
    disk_percent: float | None = None,
    net_rx_bytes: int | None = None,
    net_tx_bytes: int | None = None,
) -> Metric:
    metric = Metric(
        host_id=host_id,
        timestamp=to_utc_naive(timestamp),
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
    since: datetime | None = None,
    limit: int = 500,
) -> list[Metric]:
    query = db.query(Metric).filter(Metric.host_id == host_id)
    if since is not None:
        query = query.filter(Metric.timestamp >= to_utc_naive(since))
    return query.order_by(Metric.timestamp.desc()).limit(limit).all()


def get_latest_metric(db: Session, host_id: int) -> Metric | None:
    return (
        db.query(Metric)
        .filter(Metric.host_id == host_id)
        .order_by(Metric.timestamp.desc(), Metric.id.desc())
        .first()
    )
