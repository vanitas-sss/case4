from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.dashboard_service import list_infrastructure_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics/infra")
def infrastructure_metrics(
    period: str = Query("1h", pattern="^(1h|6h|24h|7d)$"),
    db: Session = Depends(get_db),
):
    return list_infrastructure_metrics(db, period)
