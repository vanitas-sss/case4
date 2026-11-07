from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app import stubs

router = APIRouter(tags=["hosts"])


def _find_host(host_id: int) -> dict:
    for host in stubs.HOSTS:
        if host["id"] == host_id:
            return host
    raise HTTPException(status_code=404, detail="Сервер не найден")


@router.get("/hosts")
def list_hosts(status: Optional[str] = Query(None, description="online, warning, offline или unknown")):
    # TODO: заменить на данные из БД
    if status:
        return [h for h in stubs.HOSTS if h["status"] == status]
    return stubs.HOSTS


@router.get("/hosts/{host_id}")
def get_host(host_id: int):
    # TODO: заменить на данные из БД
    host = _find_host(host_id)
    containers = [c for c in stubs.CONTAINERS if c["host_id"] == host_id]
    return {**host, "containers": containers}


@router.get("/hosts/{host_id}/metrics")
def host_metrics(host_id: int, period: str = Query("1h", pattern="^(1h|6h|24h)$")):
    # TODO: заменить на данные из БД (если точек больше 500, брать каждую N-ю)
    _find_host(host_id)
    return stubs.METRICS
