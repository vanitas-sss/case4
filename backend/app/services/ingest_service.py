from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.time import to_utc_naive
from app.models.ingest_report import IngestReport
from app.repositories import (
    availability_repo,
    containers_repo,
    events_repo,
    hosts_repo,
    metrics_repo,
    network_repo,
)
from app.schemas.ingest import ReportIn


def process(db: Session, report: ReportIn) -> int:
    data = report.model_dump()
    host_data = data["host"]
    timestamp = data["timestamp"]
    source_id = data["source_id"]
    normalized_timestamp = to_utc_naive(timestamp)

    try:
        previous_host = hosts_repo.get_by_name(db, source_id, host_data["name"])
        if (
            previous_host is not None
            and previous_host.last_seen is not None
            and normalized_timestamp <= to_utc_naive(previous_host.last_seen)
        ):
            # Пропускаем повторные и устаревшие отчёты, чтобы не перезаписать
            # более свежие данные.
            return previous_host.id

        db.add(
            IngestReport(
                source_id=source_id,
                host_name=host_data["name"],
                timestamp=normalized_timestamp,
            )
        )
        db.flush()

        previous_host_status = previous_host.status if previous_host else None

        host = hosts_repo.upsert_host(
            db=db,
            source_id=source_id,
            name=host_data["name"],
            ip=host_data.get("ip"),
            status=(
                host_data.get("status")
                or (previous_host.status if previous_host else "online")
            ),
            last_seen=timestamp,
        )

        metrics_repo.add_metric(
            db=db,
            host_id=host.id,
            timestamp=timestamp,
            cpu_percent=host_data.get("cpu_percent"),
            memory_percent=host_data.get("memory_percent"),
            disk_percent=host_data.get("disk_percent"),
            net_rx_bytes=host_data.get("net_rx_bytes"),
            net_tx_bytes=host_data.get("net_tx_bytes"),
        )

        if previous_host_status and host.status != previous_host_status:
            events_repo.create_event(
                db,
                host_id=host.id,
                event_type="host_status_changed",
                message=(
                    f"Статус сервера изменился: {previous_host_status} → {host.status}"
                ),
                timestamp=timestamp,
            )

        for item in data.get("containers") or []:
            previous_container = containers_repo.get_by_docker_id(
                db,
                host_id=host.id,
                docker_id=item["id"],
            )
            previous_container_status = (
                previous_container.status if previous_container else None
            )

            container = containers_repo.upsert_container(
                db=db,
                host_id=host.id,
                docker_id=item["id"],
                name=item["name"],
                image=item.get("image"),
                status=(
                    item.get("status")
                    or (previous_container.status if previous_container else "unknown")
                ),
                ip=item.get("ip"),
                networks=item.get("networks"),
                last_seen=timestamp,
            )

            if (
                previous_container_status
                and container.status != previous_container_status
            ):
                events_repo.create_event(
                    db,
                    host_id=host.id,
                    container_id=container.id,
                    event_type="container_status_changed",
                    message=(
                        f"Статус контейнера {container.name} изменился: "
                        f"{previous_container_status} → {container.status}"
                    ),
                    timestamp=timestamp,
                )

        availability_repo.add_check(
            db,
            host_id=host.id,
            is_online=host.status not in {"offline", "unknown"},
            checked_at=timestamp,
        )

        network_data = data.get("network")
        if network_data is not None:
            network_repo.replace_topology(
                db,
                host_id=host.id,
                nodes=network_data.get("nodes") or [],
                links=network_data.get("links") or [],
            )

        db.commit()
        return host.id
    except IntegrityError:
        db.rollback()
        duplicate = (
            db.query(IngestReport.id)
            .filter(
                IngestReport.source_id == source_id,
                IngestReport.host_name == host_data["name"],
                IngestReport.timestamp == normalized_timestamp,
            )
            .first()
        )
        if duplicate is not None:
            host = hosts_repo.get_by_name(db, source_id, host_data["name"])
            if host is not None:
                return host.id
        raise
    except Exception:
        db.rollback()
        raise
