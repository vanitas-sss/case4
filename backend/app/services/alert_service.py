from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.repositories import events_repo


def evaluate_host(db: Session, host, metric) -> None:
    """Create or resolve simple alerts from the latest received host report."""
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
                if metric.cpu_percent is not None else ""
            ),
        },
    }

    for rule_name, condition in conditions.items():
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
