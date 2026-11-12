#!/usr/bin/env python3
"""Заглушка агента: раз в N секунд шлёт массив отчётов на /api/v1/ingest.

Формат отчёта — тот же, что описан в contracts/api-examples.json.

Примеры:
  python generator.py --url http://localhost:8000/api/v1/ingest --interval 5
  python generator.py --scenario scenario_full_demo.json
  python generator.py --dry-run --once        # только напечатать JSON
Управление вручную: правьте state.json прямо во время работы.
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = Path(__file__).parent


def load_json(name):
    with open(BASE / name, encoding="utf-8") as f:
        return json.load(f)


def utc_iso(dt=None):
    dt = dt or datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


class Simulator:
    """Хранит «прошлые» значения, чтобы линии на графиках были плавными."""

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        cfg = load_json("servers.json")
        self.source_id = cfg["source_id"]
        self.servers = cfg["servers"]
        self.containers = load_json("containers.json")
        self.traffic_links = load_json("network.json")["traffic_links"]
        self.cur = {}
        self.net = {}
        for s in self.servers:
            self.cur[s["name"]] = {
                k: self.rng.uniform(*s[k]) for k in ("cpu", "memory", "disk")
            }
            self.net[s["name"]] = [10_000_000, 5_000_000]

    def _step(self, server, key, override=None):
        lo, hi = server[key]
        v = self.cur[server["name"]][key]
        if key == "cpu" and override is not None:
            target, noise = override, 1.0
        else:
            target, noise = (lo + hi) / 2, (hi - lo) / 12

        v += (target - v) * 0.15 + self.rng.uniform(-noise, noise)
        if override is None:
            v = clamp(v, lo, hi)
        else:
            v = clamp(v)
        self.cur[server["name"]][key] = v
        return round(v, 1)

    def _network(self, server, cont_status):
        name = server["name"]
        conts = self.containers.get(name, [])
        nodes = [{"id": name, "label": server["label"], "type": "server"}]
        links = []
        nets = []
        for c in conts:
            nodes.append({"id": c["name"], "label": c["name"], "type": "container"})
            running = cont_status[c["name"]] == "running"
            links.append(
                {
                    "source": name,
                    "target": c["name"],
                    "type": "host",
                    "load": self.rng.randint(5, 40) if running else 0,
                }
            )
            for n in c["networks"]:
                if n not in nets:
                    nets.append(n)
                links.append(
                    {
                        "source": c["name"],
                        "target": n,
                        "type": "network",
                        "load": self.rng.randint(5, 80) if running else 0,
                    }
                )
        for n in nets:
            nodes.append({"id": n, "label": n, "type": "network"})
        names = {c["name"]: cont_status[c["name"]] for c in conts}
        for link in self.traffic_links:
            if link["source"] in names and link["target"] in names:
                both_up = (
                    names[link["source"]] == "running"
                    and names[link["target"]] == "running"
                )
                links.append(
                    {
                        "source": link["source"],
                        "target": link["target"],
                        "type": "traffic",
                        "load": self.rng.randint(*link["load"]) if both_up else 0,
                    }
                )
        return {"nodes": nodes, "links": links}

    def build_reports(self, state, ts=None):
        """Список отчётов (по одному на сервер). Offline-серверы пропускаются."""
        reports = []
        for s in self.servers:
            name = s["name"]
            if state.get("servers", {}).get(name, "online") == "offline":
                continue
            override = (state.get("cpu_override") or {}).get(name)
            cpu = self._step(s, "cpu", override)
            mem = self._step(s, "memory")
            disk = self._step(s, "disk")
            self.net[name][0] += self.rng.randint(50_000, 900_000)
            self.net[name][1] += self.rng.randint(20_000, 400_000)
            cont_status = {
                c["name"]: (state.get("containers") or {}).get(c["name"], "running")
                for c in self.containers.get(name, [])
            }
            reports.append(
                {
                    "schema_version": "1.0",
                    "source_id": self.source_id,
                    "timestamp": utc_iso(ts),
                    "host": {
                        "name": name,
                        "ip": s["ip"],
                        "status": "online",
                        "cpu_percent": cpu,
                        "memory_percent": mem,
                        "disk_percent": disk,
                        "net_rx_bytes": self.net[name][0],
                        "net_tx_bytes": self.net[name][1],
                    },
                    "containers": [
                        {
                            "id": c["id"],
                            "name": c["name"],
                            "image": c["image"],
                            "status": cont_status[c["name"]],
                            "ip": c["ip"],
                            "networks": c["networks"],
                        }
                        for c in self.containers.get(name, [])
                    ],
                    "network": self._network(s, cont_status),
                }
            )
        return reports


def read_state():
    """state.json перечитывается на каждом шаге — можно править руками."""
    try:
        return load_json("state.json")
    except (OSError, json.JSONDecodeError) as e:
        print(f"[warn] state.json не прочитан ({e}), беру всё online")
        return {"servers": {}, "containers": {}, "cpu_override": {}}


def apply_event(state, ev):
    if "server" in ev:
        state.setdefault("servers", {})[ev["server"]] = ev["state"]
    if "container" in ev:
        state.setdefault("containers", {})[ev["container"]] = ev["state"]
    if "cpu" in ev:
        co = state.setdefault("cpu_override", {})
        for srv, val in ev["cpu"].items():
            if val is None:
                co.pop(srv, None)
            else:
                co[srv] = val


def send(url, reports, dry_run=False):
    if dry_run:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
        return True
    try:
        r = requests.post(url, json=reports, timeout=5)
        print(
            f"[{utc_iso()}] отправлено отчётов: {len(reports)} -> {r.status_code} {r.text[:120]}"
        )
        return r.ok
    except requests.RequestException as e:
        print(
            f"[{utc_iso()}] backend недоступен ({e.__class__.__name__}), повтор на след. шаге"
        )
        return False


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--url",
        default=os.environ.get("INGEST_URL", "http://localhost:8000/api/v1/ingest"),
    )
    p.add_argument("--interval", type=float, default=5.0)
    p.add_argument("--scenario", help="файл сценария, например scenario_full_demo.json")
    p.add_argument("--once", action="store_true", help="один шаг и выход")
    p.add_argument(
        "--dry-run", action="store_true", help="не отправлять, печатать JSON"
    )
    p.add_argument("--seed", type=int, default=None)
    a = p.parse_args()

    sim = Simulator(a.seed)
    events, scen_state = [], None
    if a.scenario:
        sc = load_json(a.scenario)
        events = sorted(sc["events"], key=lambda e: e["at"])
        scen_state = read_state()
        print(f"Сценарий «{sc.get('name', a.scenario)}»: {len(events)} событий")
    start = time.monotonic()

    try:
        while True:
            elapsed = time.monotonic() - start
            if scen_state is not None:
                while events and events[0]["at"] <= elapsed:
                    ev = events.pop(0)
                    apply_event(scen_state, ev)
                    print(f"[сценарий t={int(elapsed)}с] {ev}")
                state = scen_state
            else:
                state = read_state()
            reports = sim.build_reports(state)
            if reports:
                send(a.url, reports, a.dry_run)
            else:
                print(f"[{utc_iso()}] все серверы offline — ничего не отправляю")
            if a.once:
                break
            time.sleep(a.interval)
    except KeyboardInterrupt:
        print("\nОстановлено")
    return 0


if __name__ == "__main__":
    sys.exit(main())
