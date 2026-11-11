import copy
import json
from datetime import timedelta

import pytest

from tests.test_ingest import EXAMPLE, api_session_factory, client
from app.core.config import settings
from app.core.time import utc_now_naive
from app.models import Host, Alert, AvailabilityCheck
from app.services.dashboard_service import list_availability, list_topology
from app.workers.monitor import check_stale_hosts


def report_at(offset=0):
    report = copy.deepcopy(EXAMPLE)
    report[0]['timestamp'] = (utc_now_naive() + timedelta(seconds=offset)).isoformat() + 'Z'
    return report


def test_heartbeat_uses_receipt_time_and_records_outage(client, api_session_factory):
    assert client.post('/api/v1/ingest', json=EXAMPLE).json()['accepted'] == 1
    with api_session_factory() as db:
        host = db.query(Host).one()
        assert (utc_now_naive() - host.last_seen).total_seconds() < 5
        start = host.last_seen
        check_stale_hosts(db, start + timedelta(seconds=settings.WARNING_AFTER))
        assert host.status == 'warning'
        check_stale_hosts(db, start + timedelta(seconds=settings.OFFLINE_AFTER))
        assert host.status == 'offline'
        assert db.query(Alert).filter_by(rule='host_offline').count() == 0
        later = start + timedelta(seconds=settings.OFFLINE_AFTER + settings.ALERT_AFTER_OFFLINE)
        check_stale_hosts(db, later)
        check_stale_hosts(db, later + timedelta(seconds=settings.CHECK_PERIOD))
        assert db.query(Alert).filter_by(rule='host_offline', status='active').count() == 1
        assert db.query(AvailabilityCheck).filter_by(is_online=False).count() == 4
        assert list_availability(db, '24h')[0]['uptime_percent'] < 100
        nodes = list_topology(db)['nodes']
        assert next(n for n in nodes if n['type'] == 'server')['status'] == 'offline'
        assert next(n for n in nodes if n['type'] == 'container')['status'] == 'unknown'


def test_stopped_container_alert_deduplicates_and_recovers(client):
    reports = report_at()
    reports[0]['containers'][0]['status'] = 'stopped'
    client.post('/api/v1/ingest', json=reports)
    reports[0]['timestamp'] = report_at(1)[0]['timestamp']
    client.post('/api/v1/ingest', json=reports)
    alerts = client.get('/api/v1/alerts?status=active').json()
    assert len([a for a in alerts if a['rule'] == 'container_stopped']) == 1
    reports[0]['timestamp'] = report_at(2)[0]['timestamp']
    reports[0]['containers'][0]['status'] = 'running'
    client.post('/api/v1/ingest', json=reports)
    assert client.get('/api/v1/alerts?status=active').json() == []
    assert client.get('/api/v1/alerts?status=resolved').json()[0]['rule'] == 'container_stopped'


def test_import_contract_and_replay(client):
    for _ in range(2):
        response = client.post('/api/v1/import', files={'file': ('report.json', json.dumps(EXAMPLE), 'application/json')})
        assert response.status_code == 200
        assert response.json()['accepted'] == 1
    assert len(client.get('/api/v1/hosts').json()) == 1


@pytest.mark.parametrize('content,code', [('broken',400), ('{}',422), ('[1]',422), ('x' * (2*1024*1024+1),413)])
def test_import_rejects_invalid_files(client, content, code):
    assert client.post('/api/v1/import', files={'file': ('a.json', content)}).status_code == code


def test_cors_for_local_frontend(client):
    response = client.options('/api/v1/ingest', headers={
        'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type'})
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'http://localhost:5173'
