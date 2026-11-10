from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import dashboard_service

router = APIRouter(tags=["availability"])


@router.get("/availability")
def get_availability(
    period: str = Query("24h", pattern="^(1h|6h|24h|7d)$"),
    db: Session = Depends(get_db),
):
    return dashboard_service.list_availability(db, period)
