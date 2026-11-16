from datetime import datetime

from sqlalchemy.orm import Session

from app.core.time import utc_now_naive
from app.models.alert import Alert
from app.repositories import events_repo


def evaluate_host(db: Session, host, metric) -> None:
    conditions = {
        "host_offline": {
            "active": host.status == "offline",
            "severity": "critical",
            "message": f"{host.name} недоступен",
        },
        "cpu_high": {
            "active": metric.cpu_percent is not None and metric.cpu_percent >= 90,
            "severity": "warning",
            "message": (
                f"Высокая загрузка CPU на {host.name}: {metric.cpu_percent:.1f}%"
                if metric.cpu_percent is not None
                else ""
            ),
        },
    }

    for rule_name, condition in conditions.items():
        if rule_name == "cpu_high" and metric.cpu_percent is None:
            continue
        alert = (
            db.query(Alert)
            .filter(
                Alert.host_id == host.id,
                Alert.rule == rule_name,
                Alert.status == "active",
            )
            .order_by(Alert.id.desc())
            .first()
        )
        if condition["active"] and alert is None:
            db.add(
                Alert(
                    host_id=host.id,
                    rule=rule_name,
                    target=host.name,
                    severity=condition["severity"],
                    status="active",
                    message=condition["message"],
                )
            )
            events_repo.create_event(
                db,
                host_id=host.id,
                event_type="alert_opened",
                message=condition["message"],
            )
        elif not condition["active"] and alert is not None:
            alert.status = "resolved"
            alert.resolved_at = utc_now_naive()
            events_repo.create_event(
                db,
                host_id=host.id,
                event_type="alert_resolved",
                message=f"Тревога {rule_name} для {host.name} закрыта",
            )


def evaluate_container(
    db: Session,
    host,
    container,
    now: datetime | None = None,
) -> None:
    current = now or utc_now_naive()
    target = str(container.id)
    alert = (
        db.query(Alert)
        .filter_by(
            host_id=host.id, rule="container_stopped", target=target, status="active"
        )
        .first()
    )
    is_stopped = container.status in {"stopped", "exited", "dead"}
    is_online = host.status == "online"
    stopped_for = (
        (current - container.stopped_since).total_seconds()
        if container.stopped_since is not None
        else 0
    )

    if is_online and is_stopped and stopped_for >= 10 and alert is None:
        message = f"Контейнер {container.name} на {host.name} остановлен"
        db.add(
            Alert(
                host_id=host.id,
                rule="container_stopped",
                target=target,
                severity="warning",
                status="active",
                message=message,
                started_at=current,
            )
        )
        events_repo.create_event(
            db,
            host_id=host.id,
            container_id=container.id,
            event_type="alert_opened",
            message=message,
            timestamp=current,
        )
        db.flush()
    elif alert is not None and (not is_stopped or not is_online):
        alert.status = "resolved"
        alert.resolved_at = current
        events_repo.create_event(
            db,
            host_id=host.id,
            container_id=container.id,
            event_type="alert_resolved",
            message=f"Тревога контейнера {container.name} закрыта",
            timestamp=current,
        )
