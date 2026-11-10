from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import dashboard_service

router = APIRouter(tags=["alerts"])


@router.get("/alerts")
def list_alerts(
    status: str | None = Query(None, pattern="^(active|resolved)$"),
    db: Session = Depends(get_db),
):
    return dashboard_service.list_alert_rows(db, status)
