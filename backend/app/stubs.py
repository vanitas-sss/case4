HOSTS = [
    {
        "id": 1,
        "name": "server-01",
        "ip": "192.168.1.10",
        "status": "online",
        "last_seen": "2026-11-06T12:00:04Z",
        "seconds_since_seen": 4,
        "cpu_percent": 42.5,
        "memory_percent": 61.2,
        "disk_percent": 48.1,
        "containers_total": 4,
        "containers_running": 4,
        "active_alerts": 0,
    },
    {
        "id": 2,
        "name": "server-02",
        "ip": "192.168.1.11",
        "status": "offline",
        "last_seen": "2026-11-06T11:58:30Z",
        "seconds_since_seen": 94,
        "cpu_percent": 35.0,
        "memory_percent": 55.4,
        "disk_percent": 40.2,
        "containers_total": 3,
        "containers_running": 0,
        "active_alerts": 1,
    },
    {
        "id": 3,
        "name": "server-03",
        "ip": "192.168.1.12",
        "status": "warning",
        "last_seen": "2026-11-06T11:59:52Z",
        "seconds_since_seen": 12,
        "cpu_percent": 91.3,
        "memory_percent": 72.8,
        "disk_percent": 66.0,
        "containers_total": 3,
        "containers_running": 3,
        "active_alerts": 0,
    },
]

CONTAINERS = [
    {"id": 1, "host_id": 1, "host_name": "server-01", "docker_id": "c1", "name": "frontend",
     "image": "nginx:1.27", "status": "running", "ip": "172.20.0.2", "networks": ["app-net"]},
    {"id": 2, "host_id": 1, "host_name": "server-01", "docker_id": "c2", "name": "backend",
     "image": "python:3.12", "status": "running", "ip": "172.20.0.3", "networks": ["app-net", "db-net"]},
    {"id": 3, "host_id": 1, "host_name": "server-01", "docker_id": "c3", "name": "database",
     "image": "postgres:16", "status": "running", "ip": "172.21.0.2", "networks": ["db-net"]},
    {"id": 4, "host_id": 2, "host_name": "server-02", "docker_id": "c4", "name": "web",
     "image": "nginx:1.27", "status": "unknown", "ip": "172.22.0.2", "networks": ["web-net"]},
    {"id": 5, "host_id": 3, "host_name": "server-03", "docker_id": "c5", "name": "cache",
     "image": "redis:7", "status": "stopped", "ip": "172.23.0.2", "networks": ["cache-net"]},
]

METRICS = [
    {"timestamp": "2026-11-06T11:00:00Z", "cpu_percent": 38.0, "memory_percent": 60.1, "disk_percent": 48.0},
    {"timestamp": "2026-11-06T11:20:00Z", "cpu_percent": 44.2, "memory_percent": 61.0, "disk_percent": 48.1},
    {"timestamp": "2026-11-06T11:40:00Z", "cpu_percent": 51.7, "memory_percent": 62.3, "disk_percent": 48.1},
    {"timestamp": "2026-11-06T12:00:00Z", "cpu_percent": 42.5, "memory_percent": 61.2, "disk_percent": 48.1},
]

TOPOLOGY = {
    "nodes": [
        {"id": "server-01", "label": "Server 01", "type": "server", "status": "online", "ip": "192.168.1.10"},
        {"id": "frontend", "label": "frontend", "type": "container", "status": "running", "ip": "172.20.0.2"},
        {"id": "backend", "label": "backend", "type": "container", "status": "running", "ip": "172.20.0.3"},
        {"id": "database", "label": "database", "type": "container", "status": "running", "ip": "172.21.0.2"},
        {"id": "app-net", "label": "app-net", "type": "network", "status": "active", "ip": None},
        {"id": "db-net", "label": "db-net", "type": "network", "status": "active", "ip": None},
    ],
    "links": [
        {"source": "server-01", "target": "frontend", "type": "host", "load": 10},
        {"source": "server-01", "target": "backend", "type": "host", "load": 25},
        {"source": "server-01", "target": "database", "type": "host", "load": 15},
        {"source": "frontend", "target": "app-net", "type": "network", "load": 35},
        {"source": "backend", "target": "app-net", "type": "network", "load": 35},
        {"source": "backend", "target": "db-net", "type": "network", "load": 60},
        {"source": "database", "target": "db-net", "type": "network", "load": 60},
    ],
    "generated_at": "2026-11-06T12:00:05Z",
}

AVAILABILITY = [
    {"host": "server-01", "status": "online", "last_seen": "2026-11-06T12:00:04Z", "uptime_percent": 100.0},
    {"host": "server-02", "status": "offline", "last_seen": "2026-11-06T11:58:30Z", "uptime_percent": 96.4},
    {"host": "server-03", "status": "warning", "last_seen": "2026-11-06T11:59:52Z", "uptime_percent": 99.1},
]

EVENTS = [
    {"id": 3, "timestamp": "2026-11-06T11:59:10Z", "type": "alert_opened", "host": "server-02",
     "container": None, "message": "server-02 недоступен"},
    {"id": 2, "timestamp": "2026-11-06T11:58:50Z", "type": "host_offline", "host": "server-02",
     "container": None, "message": "server-02 перестал присылать данные"},
    {"id": 1, "timestamp": "2026-11-06T11:55:00Z", "type": "container_stopped", "host": "server-03",
     "container": "cache", "message": "Контейнер cache остановлен"},
]

ALERTS = [
    {"id": 5, "rule": "host_offline", "target": "server-02", "severity": "critical",
     "status": "active", "message": "server-02 недоступен",
     "started_at": "2026-11-06T11:59:10Z", "resolved_at": None},
    {"id": 4, "rule": "container_stopped", "target": "cache", "severity": "warning",
     "status": "resolved", "message": "Контейнер cache остановлен",
     "started_at": "2026-11-06T11:55:10Z", "resolved_at": "2026-11-06T11:57:00Z"},
]

SUMMARY = {
    "hosts_total": 3,
    "hosts_online": 1,
    "hosts_warning": 1,
    "hosts_offline": 1,
    "containers_total": 5,
    "containers_running": 3,
    "containers_stopped": 1,
    "active_alerts": 1,
}
