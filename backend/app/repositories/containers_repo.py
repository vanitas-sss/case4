from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.container import Container


def _utc_naive(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def upsert_container(
    db: Session,
    host_id: int,
    docker_id: str,
    name: str,
    image: Optional[str] = None,
    status: str = "unknown",
    ip: Optional[str] = None,
    networks: Optional[list[str]] = None,
    last_seen: Optional[datetime] = None,
) -> Container:
    container = (
        db.query(Container)
        .filter(Container.host_id == host_id, Container.docker_id == docker_id)
        .first()
    )
    if container is None:
        container = Container(host_id=host_id, docker_id=docker_id, name=name)
        db.add(container)

    container.name = name
    container.image = image
    container.status = status
    container.ip = ip
    container.networks = networks or []
    container.last_seen = _utc_naive(last_seen or datetime.now(timezone.utc))
    db.flush()
    return container


def list_containers(
    db: Session,
    host_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list[Container]:
    query = db.query(Container)
    if host_id is not None:
        query = query.filter(Container.host_id == host_id)
    if status:
        query = query.filter(Container.status == status)
    return query.order_by(Container.name.asc()).all()
