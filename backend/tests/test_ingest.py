import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401 — импорт нужен, чтобы зарегистрировать все модели SQLAlchemy.
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Container, Host, Metric, NetworkLink, NetworkNode

EXAMPLE = json.loads(
    (Path(__file__).parent.parent / "examples" / "ingest.example.json").read_text(
        encoding="utf-8"
    )
)


@pytest.fixture()
def api_session_factory(tmp_path):
    database_file = tmp_path / "api-test.db"
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
    testing_session = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        future=True,
    )
    try:
        yield testing_session
    finally:
        test_engine.dispose()


@pytest.fixture()
def client(api_session_factory):
    def override_get_db():
        db = api_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_valid_report_is_accepted(client):
    response = client.post("/api/v1/ingest", json=EXAMPLE)
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 1
    assert body["rejected"] == 0


def test_ingest_api_persists_report_to_database(client, api_session_factory):
    response = client.post("/api/v1/ingest", json=EXAMPLE)
    assert response.status_code == 200
    assert response.json()["accepted"] == 1

    with api_session_factory() as db:
        host = db.query(Host).filter_by(source_id="lab-01", name="server-01").one()
        assert host.ip == "192.168.1.10"

        metric = db.query(Metric).filter_by(host_id=host.id).one()
        assert metric.cpu_percent == 42.5

        container = db.query(Container).filter_by(host_id=host.id).one()
        assert container.docker_id == "c1"
        assert container.name == "frontend"

        assert db.query(NetworkNode).filter_by(host_id=host.id).count() == 3
        assert db.query(NetworkLink).filter_by(host_id=host.id).count() == 2


def test_ingest_without_host_name_is_rejected(client, api_session_factory):
    bad = copy.deepcopy(EXAMPLE)
    del bad[0]["host"]["name"]
    body = client.post("/api/v1/ingest", json=bad).json()

    assert body["accepted"] == 0
    assert body["rejected"] == 1
    assert body["errors"][0]["index"] == 0

    with api_session_factory() as db:
        assert db.query(Host).count() == 0


def test_ingest_percent_over_100_is_rejected(client):
    bad = copy.deepcopy(EXAMPLE)
    bad[0]["host"]["cpu_percent"] = 150
    body = client.post("/api/v1/ingest", json=bad).json()
    assert body["rejected"] == 1


def test_ingest_one_bad_report_does_not_block_others(client, api_session_factory):
    bad = copy.deepcopy(EXAMPLE[0])
    del bad["timestamp"]
    body = client.post("/api/v1/ingest", json=[EXAMPLE[0], bad]).json()

    assert body["accepted"] == 1
    assert body["rejected"] == 1
    assert body["errors"][0]["index"] == 1

    with api_session_factory() as db:
        assert db.query(Host).count() == 1
        assert db.query(Metric).count() == 1


def test_ingest_empty_list_is_ok(client):
    body = client.post("/api/v1/ingest", json=[]).json()
    assert body["accepted"] == 0
    assert body["rejected"] == 0


def test_ingest_object_instead_of_list_is_422(client):
    response = client.post("/api/v1/ingest", json=EXAMPLE[0])
    assert response.status_code == 422


def test_ingest_extra_fields_are_ignored(client):
    extra = copy.deepcopy(EXAMPLE)
    extra[0]["something_new"] = "ok"
    assert client.post("/api/v1/ingest", json=extra).json()["accepted"] == 1


def test_read_endpoints_return_expected_shape(client):
    first = copy.deepcopy(EXAMPLE[0])
    first["timestamp"] = datetime.now(timezone.utc).isoformat()
    first["host"]["status"] = "online"
    first["host"]["cpu_percent"] = 95.0
    second = copy.deepcopy(first)
    second["source_id"] = "lab-02"
    second["host"]["name"] = "server-02"
    second["host"]["status"] = "offline"
    second["host"]["cpu_percent"] = 10.0
    second["containers"] = []
    second["network"] = None

    ingest = client.post("/api/v1/ingest", json=[first, second])
    assert ingest.status_code == 200
    assert ingest.json()["accepted"] == 2

    hosts = client.get("/api/v1/hosts").json()
    assert len(hosts) == 2
    assert {"id", "name", "status", "last_seen", "seconds_since_seen"} <= set(hosts[0])

    assert client.get("/api/v1/hosts/1").json()["containers"]
    assert client.get("/api/v1/hosts/999").status_code == 404
    assert len(client.get("/api/v1/hosts/1/metrics?period=1h").json()) > 0
    assert client.get("/api/v1/hosts/1/metrics?period=5y").status_code == 422

    assert len(client.get("/api/v1/hosts?status=offline").json()) == 1
    assert client.get("/api/v1/containers?host_id=1").json()
    topology = client.get("/api/v1/topology?host_id=1").json()
    assert topology["nodes"] and topology["links"]
    assert len(client.get("/api/v1/availability").json()) == 2
    assert client.get("/api/v1/events?limit=1").json()
    assert len(client.get("/api/v1/alerts?status=active").json()) >= 2
    summary = client.get("/api/v1/summary").json()
    assert summary["hosts_total"] == 2
    assert summary["hosts_offline"] == 1
