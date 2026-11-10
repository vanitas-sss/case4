from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import dashboard_service

router = APIRouter(tags=["hosts"])


@router.get("/hosts")
def list_hosts(
    status: str | None = Query(None, pattern="^(online|warning|offline|unknown)$"),
    db: Session = Depends(get_db),
):
    return dashboard_service.list_host_rows(db, status)


@router.get("/hosts/{host_id}")
def get_host(host_id: int, db: Session = Depends(get_db)):
    host = dashboard_service.get_host_detail(db, host_id)
    if host is None:
        raise HTTPException(status_code=404, detail="Сервер не найден")
    return host


@router.get("/hosts/{host_id}/metrics")
def host_metrics(
    host_id: int,
    period: str = Query("1h", pattern="^(1h|6h|24h)$"),
    db: Session = Depends(get_db),
):
    if dashboard_service.get_host_detail(db, host_id) is None:
        raise HTTPException(status_code=404, detail="Сервер не найден")
    return dashboard_service.list_metric_rows(db, host_id, period)
