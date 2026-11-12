"""Адаптер: отчёт кейса 1 (Docker Network Profiler) -> наш формат ReportIn.

ВАЖНО: реальный формат их JSON пока неизвестен. Ниже — ПРЕДПОЛОЖЕНИЕ о полях
(containers / connections / dead_containers). Когда получите 1–2 настоящих
примера, поправьте только функцию `_pick` и словарь FIELD_MAP.

Адаптер не зависит от остального backend: возвращает список словарей,
которые ingest_service проверяет через ReportIn.
"""

from datetime import datetime, timezone

FIELD_MAP = {
    "containers": ["containers", "container_list"],
    "id": ["id", "container_id"],
    "name": ["name", "container_name"],
    "image": ["image"],
    "status": ["status", "state"],
    "ip": ["ip", "ip_address"],
    "networks": ["networks", "docker_networks"],
    "connections": ["connections", "links", "edges"],
    "src": ["source", "src", "from"],
    "dst": ["target", "dst", "to"],
    "count": ["count", "connections_count", "weight"],
    "dead": ["dead_containers", "inactive_containers"],
    "host": ["host", "hostname"],
}

MAX_LOAD_CONNECTIONS = 100


def _pick(d, key, default=None):
    for k in FIELD_MAP[key]:
        if isinstance(d, dict) and k in d and d[k] is not None:
            return d[k]
    return default


def _status(raw, is_dead):
    if is_dead:
        return "stopped"
    raw = str(raw or "").lower()
    if raw in ("running", "up"):
        return "running"
    if raw in ("restarting",):
        return "restarting"
    if raw in ("exited", "stopped", "dead"):
        return "stopped"
    return "unknown"


def convert(data, source_id="case1", host_name=None, host_ip=None):
    if isinstance(data, list):
        out = []
        for item in data:
            out.extend(convert(item, source_id, host_name, host_ip))
        return out

    host = host_name or _pick(data, "host") or "case1-host"
    dead = set(_pick(data, "dead", []) or [])
    ts = data.get("timestamp") or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    containers, nodes, links, nets = (
        [],
        [{"id": host, "label": host, "type": "server"}],
        [],
        set(),
    )
    for c in _pick(data, "containers", []) or []:
        name = _pick(c, "name")
        if not name:
            continue
        name = str(name).lstrip("/")
        networks = list(_pick(c, "networks", []) or [])
        status = _status(_pick(c, "status"), name in dead)
        containers.append(
            {
                "id": str(_pick(c, "id", name))[:12],
                "name": name,
                "image": _pick(c, "image"),
                "status": status,
                "ip": _pick(c, "ip"),
                "networks": networks,
            }
        )
        nodes.append({"id": name, "label": name, "type": "container"})
        links.append({"source": host, "target": name, "type": "host", "load": 0})
        for n in networks:
            nets.add(n)
            links.append({"source": name, "target": n, "type": "network", "load": 0})
    nodes += [{"id": n, "label": n, "type": "network"} for n in sorted(nets)]

    known = {n["id"] for n in nodes}
    for e in _pick(data, "connections", []) or []:
        s, t = _pick(e, "src"), _pick(e, "dst")
        if s in known and t in known:
            cnt = _pick(e, "count", 1) or 1
            load = min(100, round(cnt * 100 / MAX_LOAD_CONNECTIONS))
            links.append({"source": s, "target": t, "type": "traffic", "load": load})

    return [
        {
            "schema_version": "1.0",
            "source_id": source_id,
            "timestamp": ts,
            "host": {"name": host, "ip": host_ip, "status": "online"},
            "containers": containers,
            "network": {"nodes": nodes, "links": links},
        }
    ]


if __name__ == "__main__":
    import json
    import sys

    with open(sys.argv[1], encoding="utf-8") as f:
        print(json.dumps(convert(json.load(f)), ensure_ascii=False, indent=2))
