from sqlalchemy.orm import Session

from app.models.network import NetworkLink, NetworkNode


def replace_topology(
    db: Session,
    host_id: int,
    nodes: list[dict],
    links: list[dict],
) -> None:
    db.query(NetworkLink).filter(NetworkLink.host_id == host_id).delete(
        synchronize_session=False
    )
    db.query(NetworkNode).filter(NetworkNode.host_id == host_id).delete(
        synchronize_session=False
    )

    for item in nodes:
        db.add(
            NetworkNode(
                host_id=host_id,
                external_id=item["id"],
                label=item.get("label"),
                type=item["type"],
                status=item.get("status"),
                ip=item.get("ip"),
            )
        )

    # Сначала сохраняем узлы: связи ссылаются на них через составные
    # внешние ключи.
    db.flush()

    for item in links:
        db.add(
            NetworkLink(
                host_id=host_id,
                source_id=item["source"],
                target_id=item["target"],
                type=item["type"],
                load=item.get("load"),
            )
        )
    db.flush()


def list_nodes(db: Session, host_id: int | None = None) -> list[NetworkNode]:
    query = db.query(NetworkNode)
    if host_id is not None:
        query = query.filter(NetworkNode.host_id == host_id)
    return query.order_by(NetworkNode.id.asc()).all()


def list_links(db: Session, host_id: int | None = None) -> list[NetworkLink]:
    query = db.query(NetworkLink)
    if host_id is not None:
        query = query.filter(NetworkLink.host_id == host_id)
    return query.order_by(NetworkLink.id.asc()).all()
