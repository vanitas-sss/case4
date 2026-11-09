from datetime import datetime

from sqlalchemy.orm import Session

from app.core.time import to_utc_naive, utc_now_naive
from app.models.alert import Alert, AlertRule


def create_alert(
    db: Session,
    rule: str,
    target: str,
    severity: str = "warning",
    message: str | None = None,
    host_id: int | None = None,
    started_at: datetime | None = None,
) -> Alert:
    alert = Alert(
        host_id=host_id,
        rule=rule,
        target=target,
        severity=severity,
        message=message,
        started_at=to_utc_naive(started_at or utc_now_naive()),
    )
    db.add(alert)
    db.flush()
    return alert


def resolve_alert(
    db: Session,
    alert_id: int,
    resolved_at: datetime | None = None,
) -> Alert | None:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        return None

    alert.status = "resolved"
    alert.resolved_at = to_utc_naive(resolved_at or utc_now_naive())
    db.flush()
    return alert


def list_alerts(db: Session, status: str | None = None) -> list[Alert]:
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    return query.order_by(Alert.started_at.desc(), Alert.id.desc()).all()


def upsert_rule(
    db: Session,
    name: str,
    metric: str,
    threshold: float,
    operator: str = ">",
    duration_seconds: int = 0,
    severity: str = "warning",
    enabled: bool = True,
) -> AlertRule:
    rule = db.query(AlertRule).filter(AlertRule.name == name).first()
    if rule is None:
        rule = AlertRule(name=name, metric=metric, threshold=threshold)
        db.add(rule)

    rule.metric = metric
    rule.threshold = threshold
    rule.operator = operator
    rule.duration_seconds = duration_seconds
    rule.severity = severity
    rule.enabled = enabled
    db.flush()
    return rule
