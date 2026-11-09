from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.availability import AvailabilityCheck
from app.models.event import Event
from app.models.metric import Metric


def cleanup_old_records(
    db: Session,
    retention_days: int | None = None,
    now: datetime | None = None,
) -> dict[str, int]:
    """Delete historical metrics, events and availability checks older than retention."""
    days = settings.RETENTION_DAYS if retention_days is None else retention_days
    if days < 1:
        raise ValueError("retention_days должен быть не меньше 1")

    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is not None:
        current_time = current_time.astimezone(timezone.utc).replace(tzinfo=None)
    cutoff = current_time - timedelta(days=days)

    deleted_metrics = db.query(Metric).filter(Metric.timestamp < cutoff).delete(synchronize_session=False)
    deleted_events = db.query(Event).filter(Event.timestamp < cutoff).delete(synchronize_session=False)
    deleted_checks = (
        db.query(AvailabilityCheck)
        .filter(AvailabilityCheck.checked_at < cutoff)
        .delete(synchronize_session=False)
    )
    db.flush()
    return {
        "metrics": deleted_metrics,
        "events": deleted_events,
        "availability_checks": deleted_checks,
    }
