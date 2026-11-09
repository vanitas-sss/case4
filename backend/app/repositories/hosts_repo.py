from datetime import datetime

from sqlalchemy.orm import Session

from app.core.time import to_utc_naive, utc_now_naive
from app.models.host import Host


def get_by_id(db: Session, host_id: int) -> Host | None:
    return db.query(Host).filter(Host.id == host_id).first()


def get_by_name(db: Session, source_id: str, name: str) -> Host | None:
    return db.query(Host).filter(Host.source_id == source_id, Host.name == name).first()


def list_hosts(db: Session, status: str | None = None) -> list[Host]:
    query = db.query(Host)
    if status:
        query = query.filter(Host.status == status)
    return query.order_by(Host.name.asc()).all()


def upsert_host(
    db: Session,
    source_id: str,
    name: str,
    ip: str | None = None,
    status: str | None = None,
    last_seen: datetime | None = None,
) -> Host:
    host = get_by_name(db, source_id, name)
    if host is None:
        host = Host(source_id=source_id, name=name)
        db.add(host)

    if ip is not None:
        host.ip = ip
    if status:
        host.status = status
    host.last_seen = to_utc_naive(last_seen or utc_now_naive())
    db.flush()
    return host
