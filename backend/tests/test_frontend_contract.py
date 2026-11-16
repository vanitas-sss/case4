import copy
from datetime import timedelta

import pytest
from app.core.time import utc_now_naive
from app.models import Host, Metric

from tests.test_ingest import EXAMPLE, api_session_factory, client


def fresh_report():
    reports = copy.deepcopy(EXAMPLE)
    reports[0]["timestamp"] = utc_now_naive().isoformat() + "Z"
    return reports


def test_empty_frontend_endpoints(client):
    for path in [
        "/hosts",
        "/containers",
        "/events",
        "/alerts",
        "/sources",
        "/metrics/infra",
    ]:
        response = client.get("/api/v1" + path)
        assert response.status_code == 200
        assert response.json() == []


def test_host_details_events_and_sources(client):
    assert client.post("/api/v1/ingest", json=fresh_report()).json()["accepted"] == 1
    host = client.get("/api/v1/hosts").json()[0]
    assert host["source_id"] == EXAMPLE[0]["source_id"]
    assert host["metric_timestamp"] is not None
    detail = client.get(f"/api/v1/hosts/{host['id']}").json()
    assert detail["containers"][0]["last_seen"] is not None
    events = client.get(f"/api/v1/events?host_id={host['id']}&period=24h").json()
    assert events and all(event["host_id"] == host["id"] for event in events)
    sources = client.get("/api/v1/sources").json()
    assert sources[0]["hosts_total"] == 1
    assert sources[0]["hosts_online"] == 1


@pytest.mark.parametrize("period", ["1h", "6h", "24h", "7d"])
def test_metric_periods(client, period):
    client.post("/api/v1/ingest", json=fresh_report())
    host_id = client.get("/api/v1/hosts").json()[0]["id"]
    for path in [f"/hosts/{host_id}/metrics", "/metrics/infra"]:
        response = client.get(f"/api/v1{path}?period={period}")
        assert response.status_code == 200
        assert 0 < len(response.json()) <= 500
    assert client.get("/api/v1/metrics/infra?period=bad").status_code == 422


def test_infra_averages_hosts_equally_and_preserves_null(client, api_session_factory):
    now = utc_now_naive().replace(minute=0, second=0, microsecond=0) - timedelta(
        hours=1
    )
    with api_session_factory() as db:
        first = Host(source_id="test", name="first")
        second = Host(source_id="test", name="second")
        db.add_all([first, second])
        db.flush()
        for host, offset, value in [(first, 0, 20), (first, 1, 40), (second, 0, 90)]:
            db.add(
                Metric(
                    host_id=host.id,
                    timestamp=now + timedelta(seconds=offset),
                    cpu_percent=value,
                )
            )
        db.commit()
    rows = client.get("/api/v1/metrics/infra?period=7d").json()
    assert len(rows) == 1
    assert rows[0]["cpu_percent"] == 60
    assert rows[0]["memory_percent"] is None
    assert rows[0]["hosts_count"] == 2


def test_sources_group_multiple_hosts(client):
    reports = fresh_report()
    second = copy.deepcopy(reports[0])
    second["host"]["name"] = "second"
    reports.append(second)
    assert client.post("/api/v1/ingest", json=reports).json()["accepted"] == 2
    assert client.get("/api/v1/sources").json()[0]["hosts_total"] == 2
