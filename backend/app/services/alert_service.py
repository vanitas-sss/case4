from app.models.alert import Alert
from app.repositories import events_repo
from sqlalchemy.orm import Session


def evaluate_host(db: Session, host, metric) -> None:
    conditions = {
        "host_offline": {
            "active": host.status == "offline",
            "severity": "critical",
            "message": f"{host.name} недоступен по данным источника",
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
            from app.core.time import utc_now_naive

            alert.status = "resolved"
            alert.resolved_at = utc_now_naive()
            events_repo.create_event(
                db,
                host_id=host.id,
                event_type="alert_resolved",
                message=f"Условие тревоги {rule_name} для {host.name} больше не выполняется",
            )


def evaluate_container(db: Session, host, container) -> None:
    from app.core.time import utc_now_naive

    target = str(container.id)
    alert = (
        db.query(Alert)
        .filter_by(
            host_id=host.id, rule="container_stopped", target=target, status="active"
        )
        .first()
    )
    if host.status != "online":
        return
    if container.status in {"stopped", "exited", "dead"} and alert is None:
        message = f"Контейнер {container.name} на {host.name} остановлен"
        db.add(
            Alert(
                host_id=host.id,
                rule="container_stopped",
                target=target,
                severity="warning",
                status="active",
                message=message,
            )
        )
        events_repo.create_event(
            db,
            host_id=host.id,
            container_id=container.id,
            event_type="alert_opened",
            message=message,
        )
        db.flush()
    elif container.status == "running" and alert is not None:
        alert.status = "resolved"
        alert.resolved_at = utc_now_naive()
        events_repo.create_event(
            db,
            host_id=host.id,
            container_id=container.id,
            event_type="alert_resolved",
            message=f"Контейнер {container.name} снова работает",
        )
