import copy
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EXAMPLE = json.loads(
    (Path(__file__).parent.parent / "examples" / "ingest.example.json").read_text(encoding="utf-8")
)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ingest_valid_report_is_accepted():
    r = client.post("/api/v1/ingest", json=EXAMPLE)
    assert r.status_code == 200
    body = r.json()
    assert body["accepted"] == 1
    assert body["rejected"] == 0


def test_ingest_without_host_name_is_rejected():
    bad = copy.deepcopy(EXAMPLE)
    del bad[0]["host"]["name"]
    body = client.post("/api/v1/ingest", json=bad).json()
    assert body["accepted"] == 0
    assert body["rejected"] == 1
    assert body["errors"][0]["index"] == 0


def test_ingest_percent_over_100_is_rejected():
    bad = copy.deepcopy(EXAMPLE)
    bad[0]["host"]["cpu_percent"] = 150
    body = client.post("/api/v1/ingest", json=bad).json()
    assert body["rejected"] == 1


def test_ingest_one_bad_report_does_not_block_others():
    bad = copy.deepcopy(EXAMPLE[0])
    del bad["timestamp"]
    body = client.post("/api/v1/ingest", json=[EXAMPLE[0], bad]).json()
    assert body["accepted"] == 1
    assert body["rejected"] == 1
    assert body["errors"][0]["index"] == 1


def test_ingest_empty_list_is_ok():
    body = client.post("/api/v1/ingest", json=[]).json()
    assert body["accepted"] == 0
    assert body["rejected"] == 0


def test_ingest_object_instead_of_list_is_422():
    r = client.post("/api/v1/ingest", json=EXAMPLE[0])
    assert r.status_code == 422


def test_ingest_extra_fields_are_ignored():
    extra = copy.deepcopy(EXAMPLE)
    extra[0]["something_new"] = "ok"
    assert client.post("/api/v1/ingest", json=extra).json()["accepted"] == 1


def test_read_endpoints_return_expected_shape():
    hosts = client.get("/api/v1/hosts").json()
    assert {"id", "name", "status", "last_seen", "seconds_since_seen"} <= set(hosts[0])

    assert client.get("/api/v1/hosts/1").json()["containers"]
    assert client.get("/api/v1/hosts/999").status_code == 404
    assert len(client.get("/api/v1/hosts/1/metrics?period=1h").json()) > 0
    assert client.get("/api/v1/hosts/1/metrics?period=5y").status_code == 422

    assert len(client.get("/api/v1/hosts?status=offline").json()) == 1
    assert client.get("/api/v1/containers?host_id=1").json()
    topology = client.get("/api/v1/topology").json()
    assert topology["nodes"] and topology["links"]
    assert client.get("/api/v1/availability").json()
    assert client.get("/api/v1/events?limit=1").json()
    assert all(a["status"] == "active" for a in client.get("/api/v1/alerts?status=active").json())
    assert "hosts_total" in client.get("/api/v1/summary").json()
