from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.host import Host


def _utc_naive(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def get_by_id(db: Session, host_id: int) -> Optional[Host]:
    return db.query(Host).filter(Host.id == host_id).first()


def get_by_name(db: Session, source_id: str, name: str) -> Optional[Host]:
    return (
        db.query(Host)
        .filter(Host.source_id == source_id, Host.name == name)
        .first()
    )


def list_hosts(db: Session, status: Optional[str] = None) -> list[Host]:
    query = db.query(Host)
    if status:
        query = query.filter(Host.status == status)
    return query.order_by(Host.name.asc()).all()


def upsert_host(
    db: Session,
    source_id: str,
    name: str,
    ip: Optional[str] = None,
    status: Optional[str] = None,
    last_seen: Optional[datetime] = None,
) -> Host:
    host = get_by_name(db, source_id, name)
    if host is None:
        host = Host(source_id=source_id, name=name)
        db.add(host)

    host.ip = ip
    if status:
        host.status = status
    host.last_seen = _utc_naive(last_seen or datetime.now(timezone.utc))
    db.flush()
    return host
