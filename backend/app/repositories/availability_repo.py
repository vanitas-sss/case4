from datetime import datetime

from sqlalchemy.orm import Session

from app.core.time import to_utc_naive, utc_now_naive
from app.models.availability import AvailabilityCheck


def add_check(
    db: Session,
    host_id: int,
    is_online: bool,
    checked_at: datetime | None = None,
) -> AvailabilityCheck:
    check = AvailabilityCheck(
        host_id=host_id,
        is_online=is_online,
        checked_at=to_utc_naive(checked_at or utc_now_naive()),
    )
    db.add(check)
    db.flush()
    return check


def list_checks(
    db: Session,
    host_id: int,
    since: datetime | None = None,
    limit: int = 1000,
) -> list[AvailabilityCheck]:
    query = db.query(AvailabilityCheck).filter(AvailabilityCheck.host_id == host_id)
    if since is not None:
        query = query.filter(AvailabilityCheck.checked_at >= to_utc_naive(since))
    return query.order_by(AvailabilityCheck.checked_at.desc()).limit(limit).all()
