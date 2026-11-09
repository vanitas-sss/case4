# Database layer

The backend uses SQLAlchemy ORM with SQLite. By default, the database file is created at `backend/data/metrics.db`. The path can be changed with the `DB_PATH` environment variable.

## Tables

- `hosts` — monitored hosts, identified by `source_id + name`.
- `metrics` — time-series CPU, memory, disk and network counters for a host.
- `containers` — Docker containers belonging to a host.
- `events` — host and container status changes.
- `network_nodes`, `network_links` — the latest topology snapshot for each host.
- `availability_checks` — heartbeat/availability history.
- `alert_rules`, `alerts` — alert rule definitions and alert occurrences.

## Initialize the database

Run from the `backend` directory:

```bash
python -m app.db.init_db
```

This creates missing tables. It does not delete existing data.

## Use a database session in FastAPI

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

@router.get("/example")
def example(db: Session = Depends(get_db)):
    ...
```

## Save an incoming report

The ingest route validates the incoming JSON with `ReportIn`. The validated object can then be passed to the persistence service:

```python
from app.services.ingest_service import process

host_id = process(db, report)
```

`process` saves the host, one metric sample, containers, one availability check and the topology snapshot (when supplied). It also records an event when a known host or container changes status. The service commits each report independently and rolls it back if persistence fails.

## Repository API

Repository functions accept an existing SQLAlchemy `Session` and call `flush()`, but do not commit. The caller controls the transaction.

- `hosts_repo.get_by_id(db, host_id)`
- `hosts_repo.get_by_name(db, source_id, name)`
- `hosts_repo.list_hosts(db, status=None)`
- `hosts_repo.upsert_host(db, source_id, name, ...)`
- `metrics_repo.add_metric(db, host_id, timestamp, ...)`
- `metrics_repo.list_metrics(db, host_id, since=None, limit=500)`
- `metrics_repo.get_latest_metric(db, host_id)`
- `containers_repo.upsert_container(db, host_id, docker_id, name, ...)`
- `containers_repo.list_containers(db, host_id=None, status=None)`
- `events_repo.create_event(db, host_id, event_type, ...)`
- `events_repo.list_events(db, limit=50, event_type=None, host_id=None)`
- `network_repo.replace_topology(db, host_id, nodes, links)`
- `network_repo.list_nodes(db, host_id=None)`
- `network_repo.list_links(db, host_id=None)`
- `alerts_repo.create_alert(db, rule, target, ...)`
- `alerts_repo.resolve_alert(db, alert_id, ...)`
- `alerts_repo.list_alerts(db, status=None)`
- `alerts_repo.upsert_rule(db, name, metric, threshold, ...)`
- `availability_repo.add_check(db, host_id, is_online, ...)`
- `availability_repo.list_checks(db, host_id, since=None, limit=1000)`

## Retention cleanup

`cleanup_old_records(db, retention_days=None)` removes metrics, events and availability checks older than the configured `RETENTION_DAYS` value (7 days by default). The function does not commit; the caller controls the transaction.
