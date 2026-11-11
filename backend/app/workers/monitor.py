import asyncio
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import to_utc_naive, utc_now_naive
from app.db.session import SessionLocal
from app.models.alert import Alert
from app.models.host import Host
from app.repositories import availability_repo

from app.repositories import events_repo
from app.workers.cleanup import cleanup_old_records

logger = logging.getLogger(__name__)


def check_stale_hosts(db: Session, now: datetime | None = None) -> int:
    current = to_utc_naive(now) if now is not None else utc_now_naive()
    changed = 0
    hosts = db.query(Host).all()
    for host in hosts:
        if host.last_seen is None:
            continue
        age = max(0, (current - host.last_seen).total_seconds())
        target_status = None
        if age >= settings.OFFLINE_AFTER:
            target_status = "offline"
        elif age >= settings.WARNING_AFTER and host.status == "online":
            target_status = "warning"

        if target_status and host.status != target_status:
            previous = host.status
            host.status = target_status
            events_repo.create_event(
                db,
                host_id=host.id,
                event_type="host_status_changed",
                message=f"Статус сервера изменился: {previous} → {target_status}",
                timestamp=current,
            )
            changed += 1

        if host.status == "offline" and age >= settings.OFFLINE_AFTER + settings.ALERT_AFTER_OFFLINE:
            active = (
                db.query(Alert)
                .filter(
                    Alert.host_id == host.id,
                    Alert.rule == "host_offline",
                    Alert.status == "active",
                )
                .first()
            )
            if active is None:
                db.add(
                    Alert(
                        host_id=host.id,
                        rule="host_offline",
                        target=host.name,
                        severity="critical",
                        status="active",
                        message=f"{host.name} не присылал отчёты более {settings.OFFLINE_AFTER} секунд",
                        started_at=current,
                    )
                )
                events_repo.create_event(
                    db,
                    host_id=host.id,
                    event_type="alert_opened",
                    message=f"{host.name} недоступен: превышен таймаут heartbeat",
                    timestamp=current,
                )
        availability_repo.add_check(
            db, host_id=host.id, is_online=host.status == "online", checked_at=current
        )
    db.commit()
    return changed


def _run_monitor() -> None:
    with SessionLocal() as db:
        try:
            check_stale_hosts(db)
        except Exception:
            db.rollback()
            logger.exception("Ошибка проверки heartbeat")


def _run_cleanup() -> None:
    with SessionLocal() as db:
        try:
            cleanup_old_records(db)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Ошибка очистки истории")


async def monitor_worker() -> None:
    while True:
        await asyncio.to_thread(_run_monitor)
        await asyncio.sleep(max(1, settings.CHECK_PERIOD))


async def cleanup_worker() -> None:
    while True:
        await asyncio.sleep(3600)
        await asyncio.to_thread(_run_cleanup)
