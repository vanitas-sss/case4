from datetime import datetime

from sqlalchemy.orm import Session

from app.core.time import to_utc_naive, utc_now_naive
from app.models.container import Container


def get_by_docker_id(
    db: Session,
    host_id: int,
    docker_id: str,
) -> Container | None:
    return (
        db.query(Container)
        .filter(
            Container.host_id == host_id,
            Container.docker_id == docker_id,
        )
        .first()
    )


def upsert_container(
    db: Session,
    host_id: int,
    docker_id: str,
    name: str,
    image: str | None = None,
    status: str | None = None,
    ip: str | None = None,
    networks: list[str] | None = None,
    last_seen: datetime | None = None,
) -> Container:
    container = get_by_docker_id(db, host_id, docker_id)
    if container is None:
        container = Container(host_id=host_id, docker_id=docker_id, name=name)
        db.add(container)

    container.name = name
    if image is not None:
        container.image = image
    if status is not None:
        container.status = status
    if ip is not None:
        container.ip = ip
    if networks is not None:
        container.networks = networks
    container.last_seen = to_utc_naive(last_seen or utc_now_naive())
    db.flush()
    return container


def list_containers(
    db: Session,
    host_id: int | None = None,
    status: str | None = None,
) -> list[Container]:
    query = db.query(Container)
    if host_id is not None:
        query = query.filter(Container.host_id == host_id)
    if status:
        query = query.filter(Container.status == status)
    return query.order_by(Container.name.asc()).all()
