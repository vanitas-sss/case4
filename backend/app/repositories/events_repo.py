from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.event import Event


def _utc_naive(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def create_event(
    db: Session,
    host_id: int,
    event_type: str,
    message: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    container_id: Optional[int] = None,
) -> Event:
    event = Event(
        host_id=host_id,
        container_id=container_id,
        type=event_type,
        message=message,
        timestamp=_utc_naive(timestamp or datetime.now(timezone.utc)),
    )
    db.add(event)
    db.flush()
    return event


def list_events(
    db: Session,
    limit: int = 50,
    event_type: Optional[str] = None,
    host_id: Optional[int] = None,
) -> list[Event]:
    query = db.query(Event)
    if event_type:
        query = query.filter(Event.type == event_type)
    if host_id is not None:
        query = query.filter(Event.host_id == host_id)
    return query.order_by(Event.timestamp.desc(), Event.id.desc()).limit(limit).all()
