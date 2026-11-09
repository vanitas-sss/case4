from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.alert import Alert, AlertRule


def _utc_naive(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def create_alert(
    db: Session,
    rule: str,
    target: str,
    severity: str = "warning",
    message: Optional[str] = None,
    host_id: Optional[int] = None,
    started_at: Optional[datetime] = None,
) -> Alert:
    alert = Alert(
        host_id=host_id,
        rule=rule,
        target=target,
        severity=severity,
        message=message,
        started_at=_utc_naive(started_at or datetime.now(timezone.utc)),
    )
    db.add(alert)
    db.flush()
    return alert


def resolve_alert(db: Session, alert_id: int, resolved_at: Optional[datetime] = None) -> Optional[Alert]:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        return None
    alert.status = "resolved"
    alert.resolved_at = _utc_naive(resolved_at or datetime.now(timezone.utc))
    db.flush()
    return alert


def list_alerts(db: Session, status: Optional[str] = None) -> list[Alert]:
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    return query.order_by(Alert.started_at.desc(), Alert.id.desc()).all()


def upsert_rule(
    db: Session,
    name: str,
    metric: str,
    threshold: int,
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
