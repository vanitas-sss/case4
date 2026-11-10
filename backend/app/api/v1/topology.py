from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import dashboard_service

router = APIRouter(tags=["topology"])


@router.get("/topology")
def get_topology(
    host_id: int | None = None,
    type: str | None = Query(None, min_length=1, max_length=32),
    db: Session = Depends(get_db),
):
    return dashboard_service.list_topology(db, host_id, type)
