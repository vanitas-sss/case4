from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import to_utc_naive, utc_now_naive
from app.models.availability import AvailabilityCheck
from app.models.event import Event
from app.models.metric import Metric


def cleanup_old_records(
    db: Session,
    retention_days: int | None = None,
    now: datetime | None = None,
) -> dict[str, int]:
    """Удаляет историю метрик, событий и проверок старше срока хранения."""
    days = settings.RETENTION_DAYS if retention_days is None else retention_days
    if days < 1:
        raise ValueError("retention_days должен быть не меньше 1")

    current_time = to_utc_naive(now) if now is not None else utc_now_naive()
    cutoff = current_time - timedelta(days=days)

    deleted_metrics = (
        db.query(Metric)
        .filter(Metric.timestamp < cutoff)
        .delete(synchronize_session=False)
    )
    deleted_events = (
        db.query(Event)
        .filter(Event.timestamp < cutoff)
        .delete(synchronize_session=False)
    )
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
