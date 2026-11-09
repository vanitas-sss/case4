from datetime import datetime

from sqlalchemy.orm import Session

from app.core.time import to_utc_naive, utc_now_naive
from app.models.event import Event


def create_event(
    db: Session,
    host_id: int,
    event_type: str,
    message: str | None = None,
    timestamp: datetime | None = None,
    container_id: int | None = None,
) -> Event:
    event = Event(
        host_id=host_id,
        container_id=container_id,
        type=event_type,
        message=message,
        timestamp=to_utc_naive(timestamp or utc_now_naive()),
    )
    db.add(event)
    db.flush()
    return event


def list_events(
    db: Session,
    limit: int = 50,
    event_type: str | None = None,
    host_id: int | None = None,
) -> list[Event]:
    query = db.query(Event)
    if event_type:
        query = query.filter(Event.type == event_type)
    if host_id is not None:
        query = query.filter(Event.host_id == host_id)
    return query.order_by(Event.timestamp.desc(), Event.id.desc()).limit(limit).all()
