from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import dashboard_service

router = APIRouter(tags=["events"])


@router.get("/events")
def list_events(
    limit: int = Query(50, ge=1, le=500),
    type: str | None = None,
    host_id: int | None = None,
    db: Session = Depends(get_db),
):
    return dashboard_service.list_event_rows(db, limit, type, host_id)
