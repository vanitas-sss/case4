import copy
from datetime import timedelta

import pytest
from app.core.config import settings
from app.core.time import utc_now_naive
from app.models import Container, Host

from tests.test_ingest import EXAMPLE, api_session_factory, client


def test_registration_event_created_once(client):
    for _ in range(2):
        assert client.post("/api/v1/ingest", json=EXAMPLE).json()["accepted"] == 1
    events = client.get("/api/v1/events?type=source_registered").json()
    assert len(events) == 1


def test_future_report_cannot_block_normal_updates(client):
    bad = copy.deepcopy(EXAMPLE)
    bad[0]["timestamp"] = (utc_now_naive() + timedelta(days=365)).isoformat() + "Z"
    result = client.post("/api/v1/ingest", json=bad).json()
    assert result["rejected"] == 1
    assert result["errors"][0]["errors"][0]["loc"] == ["timestamp"]
    assert client.post("/api/v1/ingest", json=EXAMPLE).json()["accepted"] == 1
    assert client.get("/api/v1/hosts/1").json()["cpu_percent"] == 42.5


@pytest.mark.parametrize("field", ["net_rx_bytes", "net_tx_bytes"])
def test_oversized_counter_is_validation_error(client, field):
    bad = copy.deepcopy(EXAMPLE)
    bad[0]["host"][field] = 2**63
    result = client.post("/api/v1/ingest", json=bad).json()
    assert result["rejected"] == 1
    assert result["errors"][0]["errors"][0]["loc"] == ["host", field]


@pytest.mark.parametrize("stale_target", [Host, Container])
def test_stale_container_status_consistent_in_all_views(
    client, api_session_factory, stale_target
):
    client.post("/api/v1/ingest", json=EXAMPLE)
    with api_session_factory() as db:
        host = db.query(stale_target).one()
        host.last_seen = utc_now_naive() - timedelta(seconds=settings.OFFLINE_AFTER + 1)
        db.commit()
    assert client.get("/api/v1/containers").json()[0]["status"] == "unknown"
    assert client.get("/api/v1/containers?status=running").json() == []
    assert len(client.get("/api/v1/containers?status=unknown").json()) == 1
    detail = client.get("/api/v1/hosts/1").json()
    assert detail["containers_running"] == 0
    assert detail["containers"][0]["status"] == "unknown"
    summary = client.get("/api/v1/summary").json()
    assert summary["containers_running"] == 0
    assert summary["containers_stopped"] == 0
    nodes = client.get("/api/v1/topology").json()["nodes"]
    assert next(n for n in nodes if n["type"] == "container")["status"] == "unknown"
    recovered = copy.deepcopy(EXAMPLE)
    recovered[0]["timestamp"] = utc_now_naive().isoformat() + "Z"
    client.post("/api/v1/ingest", json=recovered)
    assert client.get("/api/v1/containers").json()[0]["status"] == "running"


def test_dead_container_count_matches_alert(client):
    report = copy.deepcopy(EXAMPLE)
    report[0]["containers"][0]["status"] = "dead"
    client.post("/api/v1/ingest", json=report)
    assert client.get("/api/v1/summary").json()["containers_stopped"] == 1
    assert (
        client.get("/api/v1/alerts?status=active").json()[0]["rule"]
        == "container_stopped"
    )
