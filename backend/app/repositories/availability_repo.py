from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.availability import AvailabilityCheck


def _utc_naive(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def add_check(
    db: Session,
    host_id: int,
    is_online: bool,
    checked_at: Optional[datetime] = None,
) -> AvailabilityCheck:
    check = AvailabilityCheck(
        host_id=host_id,
        is_online=is_online,
        checked_at=_utc_naive(checked_at or datetime.now(timezone.utc)),
    )
    db.add(check)
    db.flush()
    return check


def list_checks(
    db: Session,
    host_id: int,
    since: Optional[datetime] = None,
    limit: int = 1000,
) -> list[AvailabilityCheck]:
    query = db.query(AvailabilityCheck).filter(AvailabilityCheck.host_id == host_id)
    if since is not None:
        query = query.filter(AvailabilityCheck.checked_at >= _utc_naive(since))
    return query.order_by(AvailabilityCheck.checked_at.desc()).limit(limit).all()
