from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.time import utc_now_naive
from app.models.alert import Alert
from app.models.availability import AvailabilityCheck
from app.models.container import Container
from app.models.event import Event
from app.models.host import Host
from app.models.metric import Metric
from app.models.network import NetworkLink, NetworkNode
from sqlalchemy import case, func
from sqlalchemy.orm import Session


def iso_utc(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def host_status(host: Host, now: datetime | None = None) -> str:
    current = now or utc_now_naive()
    if host.last_seen is None:
        return "unknown"
    age = max(0, (current - host.last_seen.replace(tzinfo=None)).total_seconds())
    if host.status == "offline" or age >= settings.OFFLINE_AFTER:
        return "offline"
    if age >= settings.WARNING_AFTER:
        return "warning"
    return host.status or "online"


def _latest_metric(db: Session, host_id: int) -> Metric | None:
    return (
        db.query(Metric)
        .filter(Metric.host_id == host_id)
        .order_by(Metric.timestamp.desc(), Metric.id.desc())
        .first()
    )


def container_status(
    container: Container, host: Host, now: datetime | None = None
) -> str:
    current = now or utc_now_naive()
    if host_status(host, current) != "online" or container.last_seen is None:
        return "unknown"
    if (current - container.last_seen).total_seconds() >= settings.WARNING_AFTER:
        return "unknown"
    return container.status


def _container_dict(
    container: Container, host: Host, now: datetime | None = None
) -> dict:
    return {
        "id": container.id,
        "host_id": container.host_id,
        "host_name": host.name,
        "docker_id": container.docker_id,
        "name": container.name,
        "image": container.image,
        "status": container_status(container, host, now),
        "ip": container.ip,
        "networks": container.networks or [],
    }


def serialize_host(db: Session, host: Host, now: datetime | None = None) -> dict:
    metric = _latest_metric(db, host.id)
    containers = db.query(Container).filter(Container.host_id == host.id).all()
    active_alerts = (
        db.query(Alert)
        .filter(Alert.host_id == host.id, Alert.status == "active")
        .count()
    )
    return {
        "id": host.id,
        "name": host.name,
        "ip": host.ip,
        "status": host_status(host, now),
        "last_seen": iso_utc(host.last_seen),
        "seconds_since_seen": (
            max(0, int(((now or utc_now_naive()) - host.last_seen).total_seconds()))
            if host.last_seen is not None
            else None
        ),
        "cpu_percent": metric.cpu_percent if metric else None,
        "memory_percent": metric.memory_percent if metric else None,
        "disk_percent": metric.disk_percent if metric else None,
        "containers_total": len(containers),
        "containers_running": sum(
            container_status(c, host, now) == "running" for c in containers
        ),
        "active_alerts": active_alerts,
    }


def list_host_rows(db: Session, status: str | None = None) -> list[dict]:
    now = utc_now_naive()
    hosts = db.query(Host).order_by(Host.name.asc()).all()
    rows = [serialize_host(db, host, now) for host in hosts]
    return [row for row in rows if row["status"] == status] if status else rows


def get_host_detail(db: Session, host_id: int) -> dict | None:
    host = db.query(Host).filter(Host.id == host_id).first()
    if host is None:
        return None
    result = serialize_host(db, host)
    result["source_id"] = host.source_id
    result["containers"] = [
        _container_dict(c, host)
        for c in db.query(Container)
        .filter(Container.host_id == host_id)
        .order_by(Container.name)
        .all()
    ]
    return result


def list_container_rows(
    db: Session, host_id: int | None = None, status: str | None = None
) -> list[dict]:
    query = db.query(Container, Host).join(Host, Host.id == Container.host_id)
    if host_id is not None:
        query = query.filter(Container.host_id == host_id)
    now = utc_now_naive()
    rows = [
        _container_dict(container, host, now)
        for container, host in query.order_by(Container.name.asc()).all()
    ]
    return [row for row in rows if row["status"] == status] if status else rows


def list_metric_rows(db: Session, host_id: int, period: str) -> list[dict]:
    windows = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "24h": timedelta(hours=24),
    }
    since = utc_now_naive() - windows[period]
    rows = (
        db.query(Metric)
        .filter(Metric.host_id == host_id, Metric.timestamp >= since)
        .order_by(Metric.timestamp.asc(), Metric.id.asc())
        .all()
    )

    if len(rows) > 500:
        step = (len(rows) - 1) / 499
        rows = [rows[round(index * step)] for index in range(500)]
    return [
        {
            "timestamp": iso_utc(row.timestamp),
            "cpu_percent": row.cpu_percent,
            "memory_percent": row.memory_percent,
            "disk_percent": row.disk_percent,
            "net_rx_bytes": row.net_rx_bytes,
            "net_tx_bytes": row.net_tx_bytes,
        }
        for row in rows
    ]


def list_topology(
    db: Session, host_id: int | None = None, node_type: str | None = None
) -> dict:
    node_query = db.query(NetworkNode)
    link_query = db.query(NetworkLink)
    if host_id is not None:
        node_query = node_query.filter(NetworkNode.host_id == host_id)
        link_query = link_query.filter(NetworkLink.host_id == host_id)
    nodes = node_query.order_by(NetworkNode.host_id.asc(), NetworkNode.id.asc()).all()
    if node_type:
        nodes = [node for node in nodes if node.type == node_type]

    def public_id(owner_id: int, external_id: str) -> str:
        return external_id if host_id is not None else f"{owner_id}:{external_id}"

    owners = {h.id: h for h in db.query(Host).all()}
    containers = db.query(Container).all()
    container_statuses = {}
    now = utc_now_naive()
    for c in containers:
        owner = owners.get(c.host_id)
        status = container_status(c, owner, now) if owner else "unknown"
        container_statuses[(c.host_id, c.docker_id)] = status
        container_statuses[(c.host_id, c.name)] = status

    def node_status(node):
        owner = owners.get(node.host_id)
        status = host_status(owner) if owner else "unknown"
        if node.type == "server":
            return status
        if status != "online":
            return "unknown"
        if node.type == "container":
            return container_statuses.get(
                (node.host_id, node.external_id), node.status or "unknown"
            )
        return node.status or "unknown"

    allowed = {(node.host_id, node.external_id) for node in nodes}
    links = [
        link
        for link in link_query.order_by(
            NetworkLink.host_id.asc(), NetworkLink.id.asc()
        ).all()
        if (link.host_id, link.source_id) in allowed
        and (link.host_id, link.target_id) in allowed
    ]
    return {
        "nodes": [
            {
                "id": public_id(node.host_id, node.external_id),
                "external_id": node.external_id,
                "host_id": node.host_id,
                "label": node.label,
                "type": node.type,
                "status": node_status(node),
                "ip": node.ip,
            }
            for node in nodes
        ],
        "links": [
            {
                "source": public_id(link.host_id, link.source_id),
                "target": public_id(link.host_id, link.target_id),
                "type": link.type,
                "load": link.load,
                "host_id": link.host_id,
            }
            for link in links
        ],
        "generated_at": iso_utc(utc_now_naive()),
    }


def list_availability(db: Session, period: str) -> list[dict]:
    windows = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
    }
    now = utc_now_naive()
    since = now - windows[period]
    hosts = db.query(Host).order_by(Host.name.asc()).all()

    aggregates = (
        db.query(
            AvailabilityCheck.host_id,
            func.count(AvailabilityCheck.id),
            func.sum(case((AvailabilityCheck.is_online.is_(True), 1), else_=0)),
        )
        .filter(AvailabilityCheck.checked_at >= since)
        .group_by(AvailabilityCheck.host_id)
        .all()
    )
    stats = {row[0]: (int(row[1]), int(row[2] or 0)) for row in aggregates}

    result = []
    for host in hosts:
        total, successful = stats.get(host.id, (0, 0))
        result.append(
            {
                "host": host.name,
                "status": host_status(host, now),
                "last_seen": iso_utc(host.last_seen),
                "uptime_percent": round(100 * successful / total, 2) if total else None,
                "checks_total": total,
            }
        )
    return result


def list_event_rows(
    db: Session, limit: int, event_type: str | None = None, host_id: int | None = None
) -> list[dict]:
    query = db.query(Event, Host.name).join(Host, Host.id == Event.host_id)
    if event_type:
        query = query.filter(Event.type == event_type)
    if host_id is not None:
        query = query.filter(Event.host_id == host_id)
    rows = query.order_by(Event.timestamp.desc(), Event.id.desc()).limit(limit).all()
    return [
        {
            "id": event.id,
            "timestamp": iso_utc(event.timestamp),
            "type": event.type,
            "host": host_name,
            "container": event.container.name if event.container else None,
            "message": event.message,
        }
        for event, host_name in rows
    ]


def list_alert_rows(db: Session, status: str | None = None) -> list[dict]:
    query = db.query(Alert, Host.name).outerjoin(Host, Host.id == Alert.host_id)
    if status:
        query = query.filter(Alert.status == status)
    return [
        {
            "id": alert.id,
            "rule": alert.rule,
            "target": alert.target,
            "host": host_name,
            "severity": alert.severity,
            "status": alert.status,
            "message": alert.message,
            "started_at": iso_utc(alert.started_at),
            "resolved_at": iso_utc(alert.resolved_at),
        }
        for alert, host_name in query.order_by(
            Alert.started_at.desc(), Alert.id.desc()
        ).all()
    ]


def get_summary(db: Session) -> dict:
    hosts = list_host_rows(db)
    containers = list_container_rows(db)
    return {
        "hosts_total": len(hosts),
        "hosts_online": sum(row["status"] == "online" for row in hosts),
        "hosts_warning": sum(row["status"] == "warning" for row in hosts),
        "hosts_offline": sum(row["status"] == "offline" for row in hosts),
        "containers_total": len(containers),
        "containers_running": sum(row["status"] == "running" for row in containers),
        "containers_stopped": sum(
            row["status"] in {"stopped", "exited", "dead"} for row in containers
        ),
        "active_alerts": db.query(Alert).filter(Alert.status == "active").count(),
    }
