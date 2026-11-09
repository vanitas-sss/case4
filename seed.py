#!/usr/bin/env python3
"""Заливает историю метрик за N минут, чтобы графики были заполнены сразу.

  python seed.py --minutes 60 --url http://localhost:8000/api/v1/ingest
Отчёты идут с timestamp в прошлом пачками по 100 штук.
Backend считает last_seen по времени получения, поэтому seed серверы не «оживляет».
"""
import argparse
import os
from datetime import datetime, timedelta, timezone

import requests

from generator import Simulator

p = argparse.ArgumentParser()
p.add_argument("--minutes", type=int, default=60)
p.add_argument("--step", type=int, default=5, help="шаг между отчётами, сек")
p.add_argument("--url", default=os.environ.get("INGEST_URL", "http://localhost:8000/api/v1/ingest"))
p.add_argument("--dry-run", action="store_true")
a = p.parse_args()

sim = Simulator()
state = {"servers": {}, "containers": {}, "cpu_override": {}}
now = datetime.now(timezone.utc)
steps = a.minutes * 60 // a.step
batch, sent, rejected = [], 0, 0


def flush():
    global batch, sent, rejected
    if not batch:
        return
    if not a.dry_run:
        r = requests.post(a.url, json=batch, timeout=30)
        r.raise_for_status()
        rejected += r.json().get("rejected", 0)
    sent += len(batch)
    batch = []


for i in range(steps, 0, -1):
    ts = now - timedelta(seconds=i * a.step)
    batch.extend(sim.build_reports(state, ts))
    if len(batch) >= 100:
        flush()
flush()
print(f"Готово: отправлено {sent} отчётов за {a.minutes} мин, отклонено {rejected}")
