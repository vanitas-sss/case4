import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Alert, AvailabilityCheck, Container, Event, Host, Metric, NetworkLink, NetworkNode
from app.services import ingest_service
from app.workers.cleanup import cleanup_old_records
from app.schemas.ingest import ReportIn


@pytest.fixture()
def db_session(tmp_path):
    database_file = tmp_path / "test.db"
    test_engine = create_engine(
        f"sqlite:///{database_file.as_posix()}",
        connect_args={"check_same_thread": False},
        future=True,
    )
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
    example_path = (
        Path(__file__).parent.parent / "examples" / "ingest.example.json"
    )
    raw = json.loads(example_path.read_text(encoding="utf-8"))[0]
    return ReportIn.model_validate(raw)


def test_ingest_service_persists_host_metrics_containers_and_topology(db_session):
    report = _example_report()

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

    assert db_session.query(NetworkNode).filter(NetworkNode.host_id == host_id).count() == 3
    assert db_session.query(NetworkLink).filter(NetworkLink.host_id == host_id).count() == 2
    assert db_session.query(AvailabilityCheck).filter(
        AvailabilityCheck.host_id == host_id
    ).one().is_online is True


def test_repeated_ingest_updates_host_and_container_but_keeps_metric_history(db_session):
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
    assert db_session.query(AvailabilityCheck).filter(
        AvailabilityCheck.host_id == host_id
    ).count() == 2


def test_cleanup_removes_old_history_and_keeps_recent_records(db_session):
    report = _example_report()
    host_id = ingest_service.process(db_session, report)

    old_time = datetime.now(timezone.utc) - timedelta(days=10)
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
    db_session.commit()

    result = cleanup_old_records(
        db_session,
        retention_days=7,
        now=datetime.now(timezone.utc),
    )

    assert result == {"metrics": 1, "events": 1, "availability_checks": 1}
    assert db_session.query(Metric).filter(Metric.host_id == host_id).count() == 1
    assert db_session.query(Event).filter(Event.host_id == host_id).count() == 0
    assert db_session.query(AvailabilityCheck).filter(
        AvailabilityCheck.host_id == host_id
    ).count() == 1


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
