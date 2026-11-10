import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import (
    Alert,
    AvailabilityCheck,
    Container,
    Event,
    Host,
    IngestReport,
    Metric,
    NetworkLink,
    NetworkNode,
)
from app.schemas.ingest import ReportIn
from app.services import alert_service, ingest_service
from app.workers.cleanup import cleanup_old_records
from app.workers.monitor import check_stale_hosts


@pytest.fixture()
def db_session(tmp_path):
    database_file = tmp_path / "test.db"
    test_engine = create_engine(
        f"sqlite:///{database_file.as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(test_engine, "connect")
    def _enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=test_engine)
    TestingSession = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        future=True,
    )
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        test_engine.dispose()


def _example_report():
    example_path = Path(__file__).parent.parent / "examples" / "ingest.example.json"
    raw = json.loads(example_path.read_text(encoding="utf-8"))[0]
    return ReportIn.model_validate(raw)


def test_ingest_service_persists_host_metrics_containers_and_topology(db_session):
    report = _example_report()
    report.network.nodes[0].ip = "192.168.1.10"
    report.network.nodes[0].status = "online"

    host_id = ingest_service.process(db_session, report)

    host = db_session.query(Host).filter(Host.id == host_id).one()
    assert host.name == "server-01"
    assert host.source_id == "lab-01"
    assert host.ip == "192.168.1.10"

    metric = db_session.query(Metric).filter(Metric.host_id == host_id).one()
    assert metric.cpu_percent == 42.5
    assert metric.memory_percent == 61.2

    container = db_session.query(Container).filter(Container.host_id == host_id).one()
    assert container.docker_id == "c1"
    assert container.name == "frontend"
    assert container.networks == ["app-net"]

    assert (
        db_session.query(NetworkNode).filter(NetworkNode.host_id == host_id).count()
        == 3
    )
    assert (
        db_session.query(NetworkLink).filter(NetworkLink.host_id == host_id).count()
        == 2
    )
    node = (
        db_session.query(NetworkNode)
        .filter(
            NetworkNode.host_id == host_id,
            NetworkNode.external_id == "server-01",
        )
        .one()
    )
    assert node.ip == "192.168.1.10"
    assert node.status == "online"
    assert (
        db_session.query(AvailabilityCheck)
        .filter(AvailabilityCheck.host_id == host_id)
        .one()
        .is_online
        is True
    )


def test_repeated_ingest_updates_host_and_container_but_keeps_metric_history(
    db_session,
):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)

    updated = report.model_copy(deep=True)
    updated.timestamp = updated.timestamp + timedelta(seconds=5)
    updated.host.cpu_percent = 88.0
    updated.containers[0].status = "restarting"

    assert ingest_service.process(db_session, updated) == host_id

    host = db_session.query(Host).filter(Host.id == host_id).one()
    container = db_session.query(Container).filter(Container.host_id == host_id).one()

    assert host.status == "online"
    assert container.status == "restarting"
    assert db_session.query(Metric).filter(Metric.host_id == host_id).count() == 2
    assert db_session.query(Event).filter(Event.host_id == host_id).count() == 1
    assert (
        db_session.query(AvailabilityCheck)
        .filter(AvailabilityCheck.host_id == host_id)
        .count()
        == 2
    )


def test_cleanup_removes_old_history_and_keeps_recent_records(db_session):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)

    old_time = datetime.now(UTC) - timedelta(days=10)
    db_session.add(
        Metric(
            host_id=host_id,
            timestamp=old_time.replace(tzinfo=None),
            cpu_percent=1.0,
        )
    )
    db_session.add(
        Event(
            host_id=host_id,
            timestamp=old_time.replace(tzinfo=None),
            type="old_event",
            message="old",
        )
    )
    db_session.add(
        AvailabilityCheck(
            host_id=host_id,
            checked_at=old_time.replace(tzinfo=None),
            is_online=False,
        )
    )
    db_session.add(
        IngestReport(
            source_id="old-source",
            host_name="old-host",
            timestamp=old_time.replace(tzinfo=None),
        )
    )
    db_session.commit()

    result = cleanup_old_records(
        db_session,
        retention_days=7,
        now=datetime.now(UTC),
    )

    assert result == {"metrics": 1, "events": 1, "availability_checks": 1}
    assert db_session.query(Metric).filter(Metric.host_id == host_id).count() == 1
    assert db_session.query(Event).filter(Event.host_id == host_id).count() == 0
    assert (
        db_session.query(IngestReport)
        .filter(IngestReport.source_id == "old-source")
        .count()
        == 0
    )
    assert (
        db_session.query(AvailabilityCheck)
        .filter(AvailabilityCheck.host_id == host_id)
        .count()
        == 1
    )


def test_ingest_rolls_back_all_changes_on_failure(db_session, monkeypatch):
    report = _example_report()

    def fail_add_check(*args, **kwargs):
        raise RuntimeError("test failure")

    monkeypatch.setattr(
        "app.services.ingest_service.availability_repo.add_check",
        fail_add_check,
    )

    with pytest.raises(RuntimeError, match="test failure"):
        ingest_service.process(db_session, report)

    assert db_session.query(Host).count() == 0
    assert db_session.query(Metric).count() == 0


def test_report_rejects_unknown_host_status():
    report = _example_report().model_dump()
    report["host"]["status"] = "available-ish"

    with pytest.raises(ValueError):
        ReportIn.model_validate(report)


def test_report_rejects_blank_required_identifiers():
    report = _example_report().model_dump()
    report["source_id"] = "   "

    with pytest.raises(ValueError):
        ReportIn.model_validate(report)


def test_report_rejects_duplicate_container_ids():
    report = _example_report().model_dump()
    report["containers"].append(report["containers"][0].copy())

    with pytest.raises(ValueError, match="контейнеров"):
        ReportIn.model_validate(report)


def test_report_rejects_duplicate_topology_nodes():
    report = _example_report().model_dump()
    report["network"]["nodes"].append(report["network"]["nodes"][0].copy())

    with pytest.raises(ValueError, match="узлов"):
        ReportIn.model_validate(report)


def test_report_rejects_links_to_missing_topology_nodes():
    report = _example_report().model_dump()
    report["network"]["links"][0]["target"] = "missing-node"

    with pytest.raises(ValueError, match="отсутствующий узел"):
        ReportIn.model_validate(report)


def test_report_rejects_duplicate_topology_links():
    report = _example_report().model_dump()
    report["network"]["links"].append(report["network"]["links"][0].copy())

    with pytest.raises(ValueError, match="не должны повторяться"):
        ReportIn.model_validate(report)


def test_database_rejects_duplicate_report_keys(db_session):
    report = _example_report()
    ingest_service.process(db_session, report)
    db_session.add(
        IngestReport(
            source_id=report.source_id,
            host_name=report.host.name,
            timestamp=report.timestamp.replace(tzinfo=None),
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_database_enforces_foreign_keys(db_session):
    db_session.add(
        Metric(
            host_id=999,
            timestamp=datetime(2026, 11, 9, 12, 0),
            cpu_percent=10.0,
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_deleting_host_applies_cascade_and_set_null_rules(db_session):
    host_id = ingest_service.process(db_session, _example_report())
    alert = Alert(
        host_id=host_id,
        rule="cpu_high",
        target="server-01",
        severity="warning",
        status="active",
    )
    db_session.add(alert)
    db_session.commit()
    alert_id = alert.id

    host = db_session.query(Host).filter(Host.id == host_id).one()
    db_session.delete(host)
    db_session.commit()

    assert db_session.query(Host).filter(Host.id == host_id).count() == 0
    assert db_session.query(Metric).filter(Metric.host_id == host_id).count() == 0
    assert db_session.query(Container).filter(Container.host_id == host_id).count() == 0
    assert db_session.query(Event).filter(Event.host_id == host_id).count() == 0
    assert (
        db_session.query(NetworkNode).filter(NetworkNode.host_id == host_id).count()
        == 0
    )
    assert (
        db_session.query(NetworkLink).filter(NetworkLink.host_id == host_id).count()
        == 0
    )
    assert (
        db_session.query(AvailabilityCheck)
        .filter(AvailabilityCheck.host_id == host_id)
        .count()
        == 0
    )

    preserved_alert = db_session.query(Alert).filter(Alert.id == alert_id).one()
    assert preserved_alert.host_id is None


def test_new_topology_replaces_previous_snapshot(db_session):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)

    updated = report.model_copy(deep=True)
    updated.timestamp = updated.timestamp + timedelta(seconds=5)
    updated.network.nodes = [updated.network.nodes[0]]
    updated.network.links = []

    ingest_service.process(db_session, updated)

    nodes = db_session.query(NetworkNode).filter(NetworkNode.host_id == host_id).all()
    links = db_session.query(NetworkLink).filter(NetworkLink.host_id == host_id).all()

    assert len(nodes) == 1
    assert nodes[0].external_id == "server-01"
    assert links == []


def test_report_without_topology_keeps_previous_snapshot(db_session):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)

    updated = report.model_copy(deep=True)
    updated.timestamp = updated.timestamp + timedelta(seconds=5)
    updated.network = None
    ingest_service.process(db_session, updated)

    assert (
        db_session.query(NetworkNode).filter(NetworkNode.host_id == host_id).count()
        == 3
    )
    assert (
        db_session.query(NetworkLink).filter(NetworkLink.host_id == host_id).count()
        == 2
    )


def test_replayed_report_is_idempotent(db_session):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)

    assert ingest_service.process(db_session, report) == host_id

    assert db_session.query(Host).count() == 1
    assert db_session.query(Metric).filter(Metric.host_id == host_id).count() == 1
    assert (
        db_session.query(AvailabilityCheck)
        .filter(AvailabilityCheck.host_id == host_id)
        .count()
        == 1
    )


def test_duplicate_report_key_does_not_create_another_metric(db_session):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)
    host = db_session.query(Host).filter(Host.id == host_id).one()
    host.last_seen = report.timestamp - timedelta(seconds=1)
    db_session.commit()

    assert ingest_service.process(db_session, report) == host_id
    assert db_session.query(Metric).filter(Metric.host_id == host_id).count() == 1


def test_out_of_order_report_does_not_overwrite_newer_state(db_session):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)

    newer = report.model_copy(deep=True)
    newer.timestamp += timedelta(minutes=2)
    newer.host.cpu_percent = 91.0
    newer.host.status = "online"
    ingest_service.process(db_session, newer)

    stale = report.model_copy(deep=True)
    stale.timestamp += timedelta(minutes=1)
    stale.host.cpu_percent = 5.0
    stale.host.status = "offline"
    ingest_service.process(db_session, stale)

    host = db_session.query(Host).filter(Host.id == host_id).one()
    metrics = db_session.query(Metric).filter(Metric.host_id == host_id).all()

    assert host.status == "online"
    assert host.last_seen == newer.timestamp.replace(tzinfo=None)
    assert len(metrics) == 2
    assert max(metric.timestamp for metric in metrics) == newer.timestamp.replace(
        tzinfo=None
    )


def test_missing_optional_network_fields_do_not_erase_known_values(db_session):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)

    updated = report.model_copy(deep=True)
    updated.timestamp += timedelta(seconds=5)
    updated.host.ip = None
    updated.containers[0].image = None
    updated.containers[0].ip = None
    ingest_service.process(db_session, updated)

    host = db_session.query(Host).filter(Host.id == host_id).one()
    container = db_session.query(Container).filter(Container.host_id == host_id).one()

    assert host.ip == "192.168.1.10"
    assert container.image is not None
    assert container.ip is not None


def test_missing_status_does_not_reset_known_host_or_container_status(db_session):
    report = _example_report()
    report.host.status = "offline"
    report.containers[0].status = "running"
    host_id = ingest_service.process(db_session, report)

    updated = report.model_copy(deep=True)
    updated.timestamp += timedelta(seconds=5)
    updated.host.status = None
    updated.containers[0].status = None
    ingest_service.process(db_session, updated)

    host = db_session.query(Host).filter(Host.id == host_id).one()
    container = db_session.query(Container).filter(Container.host_id == host_id).one()

    assert host.status == "offline"
    assert container.status == "running"


def test_missing_container_networks_do_not_clear_known_networks(db_session):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)

    updated = report.model_copy(deep=True)
    updated.timestamp += timedelta(seconds=5)
    updated.containers[0].networks = None
    ingest_service.process(db_session, updated)

    container = db_session.query(Container).filter(Container.host_id == host_id).one()

    assert container.networks == ["app-net"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("cpu_percent", 101.0),
        ("memory_percent", -1.0),
        ("disk_percent", 101.0),
        ("net_rx_bytes", -1),
        ("net_tx_bytes", -1),
    ],
)
def test_database_rejects_out_of_range_metrics(db_session, field, value):
    host_id = ingest_service.process(db_session, _example_report())
    db_session.add(
        Metric(
            host_id=host_id,
            timestamp=datetime(2026, 11, 9, 12, 0),
            **{field: value},
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


@pytest.mark.parametrize(
    "source_id,target_id",
    [
        ("missing-node", "server-01"),
        ("server-01", "missing-node"),
    ],
)
def test_database_rejects_network_links_to_missing_nodes(
    db_session, source_id, target_id
):
    host_id = ingest_service.process(db_session, _example_report())
    db_session.add(
        NetworkLink(
            host_id=host_id,
            source_id=source_id,
            target_id=target_id,
            type="traffic",
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_database_rejects_network_load_outside_range(db_session):
    host_id = ingest_service.process(db_session, _example_report())
    db_session.add(
        NetworkLink(
            host_id=host_id,
            source_id="server-01",
            target_id="frontend",
            type="traffic",
            load=150.0,
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_deleting_topology_node_cascades_its_links(db_session):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)
    node = (
        db_session.query(NetworkNode)
        .filter(
            NetworkNode.host_id == host_id,
            NetworkNode.external_id == "frontend",
        )
        .one()
    )

    db_session.delete(node)
    db_session.commit()

    remaining_links = (
        db_session.query(NetworkLink).filter(NetworkLink.host_id == host_id).all()
    )
    assert all(
        link.source_id != "frontend" and link.target_id != "frontend"
        for link in remaining_links
    )


def test_cpu_alert_is_opened_and_resolved_when_metric_recovers(db_session):
    report = _example_report()
    report.host.cpu_percent = 95.0
    host_id = ingest_service.process(db_session, report)

    alert = (
        db_session.query(Alert)
        .filter(Alert.host_id == host_id, Alert.rule == "cpu_high")
        .one()
    )
    assert alert.status == "active"
    assert alert.severity == "warning"

    recovered = report.model_copy(deep=True)
    recovered.timestamp += timedelta(seconds=5)
    recovered.host.cpu_percent = 40.0
    ingest_service.process(db_session, recovered)

    db_session.refresh(alert)
    assert alert.status == "resolved"
    assert alert.resolved_at is not None
    assert (
        db_session.query(Event)
        .filter(Event.host_id == host_id, Event.type == "alert_resolved")
        .count()
        == 1
    )


def test_offline_host_creates_critical_alert(db_session):
    report = _example_report()
    report.host.status = "offline"
    host_id = ingest_service.process(db_session, report)

    alert = (
        db_session.query(Alert)
        .filter(Alert.host_id == host_id, Alert.rule == "host_offline")
        .one()
    )
    assert alert.status == "active"
    assert alert.severity == "critical"



def test_heartbeat_worker_marks_host_offline_and_ingest_resolves_alert(db_session):
    report = _example_report()
    report.timestamp = datetime.now(UTC) - timedelta(seconds=200)
    report.host.status = "online"
    host_id = ingest_service.process(db_session, report)

    changed = check_stale_hosts(db_session, now=datetime.now(UTC))
    assert changed == 1

    host = db_session.query(Host).filter(Host.id == host_id).one()
    assert host.status == "offline"
    offline_alert = (
        db_session.query(Alert)
        .filter(Alert.host_id == host_id, Alert.rule == "host_offline")
        .one()
    )
    assert offline_alert.status == "active"

    recovered = report.model_copy(deep=True)
    recovered.timestamp = datetime.now(UTC)
    recovered.host.status = None
    ingest_service.process(db_session, recovered)

    db_session.refresh(host)
    db_session.refresh(offline_alert)
    assert host.status == "online"
    assert offline_alert.status == "resolved"
